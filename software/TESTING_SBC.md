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

The TWO lEDS should be on at startup, then when operation commences the second LED should be flashing.

RESET 
    pigs spix 0 0x8F 0x01   # 0b10001111 0b00000001

READ sample delay:         ret = spi.transfer((0b00001100,0x0,0b0000000))
    pigs spix 0 0x0C 0x00 0x00 

    
## Diagnose MODE1

Get the url (https://api.elec.ac.nz/tart/tart3-test/api/v1/status/fpga) and check status.

```
AQ Stream: 15
AQ System: 
    512MB: 0 
    SDRam ready:
    enabled: 1
    error: 0
    overflow: 1
    state: 3

SPI Stats: 
    FIFO overflow:
    FIFO underrun:
    SPI_busy:1
    
SYS Stats:
    ACQ en: 1
    cap debug: 0
    cap en: 1
    state: 3
    viz en: 0
    viz pend: 0

TC Centre:
    centre: 1
    delay: 0
    drift: 0
    invert: 0
    
TC Debug:
    count: 0
    debug: 0
    num antenna: 24
    shift: 0
TC Status
    delta: 14
    phase: 2
TC System
    enabled: 1
    error: 0
    locked: 1
    source: 0
VX Debug
    limp: 1
    stuck: 0

VX Status
    accessed: 1
    available: 0
    bank: 0
    overflow: 0

VX Stream
    data: 2
VX System
    block size: 20
    enabled: 0
    overwrite: 0
```
