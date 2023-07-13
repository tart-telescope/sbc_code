## Quartz64 Installation 

For the Pine64 single board computer, there are some specific hardware requirements.


## SPI Device Tree

See https://github.com/CounterPillow/overlay-examples/blob/main/quartz64b/mcp4821.dts

    sudo apt install -y devicetrees-plebian-quartz64
    make

Simply place the .dtbo file into the /boot/dtbo/ directory, creating said directory if it doesn't already exist. 
Then run 

    sudo u-boot-update 

and the device tree blob overlay will be picked up, and included in your extlinux.conf. 
