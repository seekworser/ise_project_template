import yaml
import invoke


def get_project_parameter(*keys):
    param = yaml.load(open(PROJECT_YAML_FILE_NAME, "r+"))
    for item in keys:
        param = param[item]
    return param

def set_default_on_keyerror(target_dict, target_key, default_value):
    try:
        retval = target_dict[target_key]
    except KeyError as e:
        print("\033[93mWarning\033[0m: key name {e} not found in project yaml. Skip this parameter.".format(e=e))
        retval = default_value
    return retval

def create_project_file():
    content = ""
    for item in get_project_parameter(SRC_FILES_KEY):
        language = set_default_on_keyerror(item, LANGUAGE_KEY, LANGUAGE_DEFAULT)
        library = set_default_on_keyerror(item, LIBRARY_KEY, LIBRARY_DEFAULT)
        filename = item[FILE_NAME_KEY]
        content += "{language:s} {library:s} .{srcdir:s}{filename:s}\n".format(
            language=language,
            library=library,
            srcdir=SRCDIR,
            filename=filename,
        )
    with open(PRJ_FILE_NAME, "w") as f:
        f.write(content)
    return

def part_specifier():
    part_dict = get_project_parameter(PART_KEY)
    architecture = set_default_on_keyerror(part_dict, ARCHITECTURE_KEY, None)
    if architecture is not None:
        return architecture
    device = part_dict[DEVICE_KEY]
    package = set_default_on_keyerror(part_dict, PACKAGE_KEY, "")
    speed = set_default_on_keyerror(part_dict, SPEED_KEY, "")
    return "{device:s}{package:s}{speed:s}".format(
        device=device,
        package=package,
        speed=str(speed)
    )

def create_xst_file():
    part = part_specifier()
    content = "run -ifn {prj_file_name:s} -ifmt mixed -top {top_module} -ofn {outdir:s}{top_module:s}.ngc -ofmt NGC -p {part:s}\n".format(
        prj_file_name=PRJ_FILE_NAME,
        top_module=get_project_parameter(TOP_MODULE_KEY),
        outdir=OUTDIR,
        part=part,
    )
    with open(OUTDIR + get_project_parameter(TOP_MODULE_KEY) + ".xst", "w") as f:
        f.write(content)
    return

@invoke.task
def xst(c):
    create_project_file()
    create_xst_file()
    c.run(
        "docker run --rm -i -v $(PWD):/project seekworser/ise_webpack:latest sh <<_EOT_\n"
        "cd /project\n"
        "{ise_base:s}xst -ifn {outdir:s}{top_module:s}.xst -ofn {logdir:s}{top_module:s}_xst.log\n"
        "rm -rf *.srp *.lso xst _xmsgs {outdir:s}*.xst {outdir:s}*.prj\n"
        "_EOT_\n".format(
            ise_base=ISE_BASE,
            top_module=get_project_parameter(TOP_MODULE_KEY),
            outdir=OUTDIR,
            logdir=LOGDIR,
        )
    )
    return

@invoke.task
def ngdbuild(c):
    part = part_specifier()
    ucf = get_project_parameter(UCF_FILE_KEY)
    c.run(
        "docker run --rm -i -v $(PWD):/project seekworser/ise_webpack:latest sh <<_EOT_\n"
        "cd /project\n"
        "{ise_base:s}ngdbuild -p {part:s} -uc {srcdir:s}{ucf:s} -verbose {outdir:s}{top_module:s}.ngc {outdir:s}{top_module:s}.ngd\n"
        "mv netlist.lst out\n"
        "mv {outdir:s}{top_module:s}.bld {logdir:s}{top_module:s}_ngdbuild.log\n"
        "rm -rf _xmsgs xlnx_auto_0_xdb {outdir:s}*.xrpt\n"
        "_EOT_".format(
            ise_base=ISE_BASE,
            part=part,
            ucf=ucf,
            top_module=get_project_parameter(TOP_MODULE_KEY),
            outdir=OUTDIR,
            srcdir=SRCDIR,
            logdir=LOGDIR,
        )
    )
    return

@invoke.task
def map(c):
    part = part_specifier()
    c.run(
        "docker run --rm -i -v $(PWD):/project seekworser/ise_webpack:latest sh <<_EOT_\n"
        "cd /project\n"
        "{ise_base:s}map -detail -w -p {part:s} -logic_opt on -o {outdir:s}{top_module:s}_map.ncd {outdir:s}{top_module:s}.ngd {outdir:s}{top_module:s}.pcf\n"
        "mv {outdir:s}*.mrp {logdir:s}{top_module:s}_map.log\n"
        "rm -rf _xmsgs {outdir:s}*.map {outdir:s}*.xrpt {outdir:s}*.ngm xilinx_device_details.xml\n"
        "_EOT_".format(
            ise_base=ISE_BASE,
            part=part,
            top_module=get_project_parameter(TOP_MODULE_KEY),
            outdir=OUTDIR,
            logdir=LOGDIR,
        )
    )
    return

@invoke.task
def par(c):
    c.run(
        "docker run --rm -i -v $(PWD):/project seekworser/ise_webpack:latest sh <<_EOT_\n"
        "cd /project\n"
        "{ise_base:s}par -w -mt 4 -ol high {outdir:s}{top_module:s}_map.ncd {outdir:s}{top_module:s}.ncd {outdir:s}{top_module:s}.pcf\n"
        "rm -rf _xmsgs par_usage_statistics.html *.xrpt {outdir:s}*.ptwx {outdir:s}*.txt {outdir:s}*.unroutes {outdir:s}*.xpi {outdir:s}*.pad\n"
        "mv {outdir:s}*.par {logdir:s}{top_module:s}_par.log\n"
        "_EOT_".format(
            ise_base=ISE_BASE,
            top_module=get_project_parameter(TOP_MODULE_KEY),
            outdir=OUTDIR,
            logdir=LOGDIR,
        )
    )
    return

@invoke.task
def bitgen(c):
    c.run(
        "docker run --rm -i -v $(PWD):/project seekworser/ise_webpack:latest sh <<_EOT_\n"
        "cd /project\n"
        "{ise_base:s}bitgen -w {outdir:s}{top_module:s}.ncd {top_module:s}.bit {outdir:s}{top_module:s}.pcf\n"
        "mv *.drc {logdir:s}{top_module:s}_drc.log\n"
        "mv *.bgn {logdir:s}{top_module:s}_bitgen.log\n"
        "rm -rf *.xwbt _xmsgs xilinx_device_details.xml *.xrpt\n"
        "_EOT_".format(
            ise_base=ISE_BASE,
            top_module=get_project_parameter(TOP_MODULE_KEY),
            outdir=OUTDIR,
            logdir=LOGDIR,
        )
    )
    return

def gdhl_compile(c, file_name, entity_names):
    with c.cd("{testdir:s}".format(testdir=TESTDIR)):
        c.run("ghdl -a --ieee=synopsys .{srcdir:s}{file_name:s}".format(
            srcdir=SRCDIR,
            file_name=file_name,
        ))
        for entity_name in entity_names:
            c.run("ghdl -e --ieee=synopsys {entity_name:s}".format(
                srcdir=SRCDIR,
                entity_name=entity_name,
            ))
    return

def ghdl_test_runner(c, entity_name):
    with c.cd("{testdir:s}".format(testdir=TESTDIR)):
        c.run("ghdl -r {entity_name:s} --vcd={entity_name:s}.vcd".format(
            entity_name=entity_name,
        ))
    return

def ghdl_clean(c):
    c.run("rm {testdir:s}*.o {testdir:s}*.cf".format(testdir=TESTDIR))

@invoke.task(iterable=["entity_name"])
def test(c, entity_name):
    if not entity_name:
        entity_name = []
        for item in get_project_parameter(TEST_FILES_KEY):
            entity_name += item[ENTITY_NAMES_KEY]
    for item in get_project_parameter(SRC_FILES_KEY):
        gdhl_compile(c, item[FILE_NAME_KEY], item[ENTITY_NAMES_KEY])
    for item in get_project_parameter(TEST_FILES_KEY):
        gdhl_compile(c, item[FILE_NAME_KEY], item[ENTITY_NAMES_KEY])
    for item in entity_name:
        ghdl_test_runner(c, item)
    ghdl_clean(c)
    return

@invoke.task
def build(c):
    xst(c)
    ngdbuild(c)
    map(c)
    par(c)
    bitgen(c)
    return


OUTDIR = "./out/"
SRCDIR = "./src/"
LOGDIR = "./log/"
TESTDIR = "./test/"
PROJECT_YAML_FILE_NAME = SRCDIR + "project.yaml"

LANGUAGE_DEFAULT = "vhdl"
LIBRARY_DEFAULT = "work"

SRC_FILES_KEY = "src_files"
LANGUAGE_KEY = "language"
LIBRARY_KEY = "library"
FILE_NAME_KEY = "file_name"

TEST_FILES_KEY = "test_files"
ENTITY_NAMES_KEY = "entity_names"

TOP_MODULE_KEY = "top_module"
PART_KEY = "part"
ARCHITECTURE_KEY = "architecture"
DEVICE_KEY = "device"
PACKAGE_KEY = "package"
SPEED_KEY = "speed"
UCF_FILE_KEY = "ucf_file"

PRJ_FILE_NAME = OUTDIR + get_project_parameter(TOP_MODULE_KEY) + ".prj"
OPTIONS_FILE_NAME = OUTDIR + get_project_parameter(TOP_MODULE_KEY) + ".options"

ISE_BASE = "/opt/Xilinx/14.7/ISE_DS/ISE/bin/lin64/"
