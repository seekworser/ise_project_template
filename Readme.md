# Description

Template and sample code for Xilinx ISE project.

# Requiremet

- docker
- python 3.x
- invoke (python package)

# Usage

## Start project
```bash
git clone https://github.com/seekworser/ise_project_template.git <your_project_name>
cd <your_project_name>
```

## Building process

To build, you can use
```bash
invoke build
```
or other commands shown in below.
- build
- xst
- ngdbuild
- map
- par
- bitgen
- test [-e entity]

# Notification

In building process,
invoke download the docker image
whose size is larger than 30 GB.
So you are required to have the enough space on your computer.

# For Gadget Factory devices

If you are using Gadget Factory device,
you can use Papilio-Loader (or its CLI, papilio-prog) to write the bitstream (`.bit`) file to a target device.
if you want to write the `your_project.bit` file, you can use
```bash
papilio-prog -v -f your_project.bit
```
or, you can write to SPI Flash by
```bash
cp /path/to/macosx/bscan_spi_<your_device_name>.bit .
papilio-prog -v -f your_project.bit -b bscan_spi_<your_device_name>.bit
```
This bitstream is located in `/Applications/GadgetFactory/Papilio-Loader/Java-GUI/programmer/macosx/` on MacOS (default installation).
