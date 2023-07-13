INCLUDE_DIR ?= linux/include
DTS = $(shell find -name '*.dts')
DTBS = $(addprefix build/,$(addsuffix .dtbo,$(basename $(DTS))))
DTC ?= dtc
DTCFLAGS ?= -@
CPPFLAGS ?= -E -nostdinc -I$(INCLUDE_DIR) -undef -D__DTS__ -x assembler-with-cpp

all: 
	dtc -O dtb -o tart.dtbo -@ tart.dts

.PHONY: clean all

