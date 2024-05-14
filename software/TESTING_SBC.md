# TARTING the Single Board computer

Information on testing the SPI connection. MODE1 (POL = 0, PHA = 1) SPI master, and the data bit-width is set to 8-bits.

    apt install pigpiod pigpio-tools
    sudo pigpiod
    pigs spio 0 100000 1
    pigs spix 0 0x55 0x11 0xFF 0xAA
    ...
    pigs spic 0

## Step 1. Check the clock to the FPGA

This should be 16.368 MHz on an oscilloscope.

## TART SPI COMMANDS

RESET 
    pigs spix 0 0x8F 0x01   # 0b10001111 0b00000001

READ sample delay:         ret = spi.transfer((0b00001100,0x0,0b0000000))
    pigs spix 0 0x0C 0x00 0x00 
