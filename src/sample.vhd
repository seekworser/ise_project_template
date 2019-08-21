library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

entity sample is
    port (
        a : out  std_logic_vector (8 downto 0);
        clk : in std_logic
    );
end sample;

architecture behavior of sample is
    signal counter : std_logic_vector(21 downto 0) := (others => '0');
begin
    count: process(clk)
    begin
        if rising_edge(clk) then
            counter <= counter+1;
        end if;
    end process;
    a <= counter(21 downto 13);
end behavior;