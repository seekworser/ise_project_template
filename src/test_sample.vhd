library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

entity test_sample is
end test_sample;

architecture behavior of test_sample is
    component sample is
        port (
            clk: in std_logic;
            a: out std_logic_vector (8 downto 0)
        );
    end component;
    signal clk: std_logic;
    signal a: std_logic_vector (8 downto 0);
begin 
    u1: sample port map(
        clk => clk,
        a => a
    );
    process
    begin
        for i in 0 to 1000000 loop
            clk <= '1';
            wait for 16.25 ns;
            clk <= '0';
            wait for 16.25 ns;
        end loop;
        wait;
    end process;
end behavior;

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

entity test_sample2 is
end test_sample2;

architecture behavior of test_sample2 is
    component sample is
        port (
            clk: in std_logic;
            a: out std_logic_vector (8 downto 0)
        );
    end component;
    signal clk: std_logic;
    signal a: std_logic_vector (8 downto 0);
begin 
    u1: sample port map(
        clk => clk,
        a => a
    );
    process
    begin
        for i in 0 to 1000 loop
            clk <= '1';
            wait for 16.25 us;
            clk <= '0';
            wait for 16.25 us;
        end loop;
        wait;
    end process;
end behavior;
