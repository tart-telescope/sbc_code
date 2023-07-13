INCLUDE_DIR ?= linux-source-6.1/include
DTS = $(shell find quartz64b -name '*.dts')
DTBS = $(addprefix build/,$(addsuffix .dtbo,$(basename $(DTS))))
DTC ?= dtc
DTCFLAGS ?= -@
CPPFLAGS ?= -E -nostdinc -I$(INCLUDE_DIR) -undef -D__DTS__ -x assembler-with-cpp

all: build/quartz64b  $(DTBS)
	
install:
	sudo cp tart.dtbo /boot/dtbo
	sudo u-boot-update

build:
	mkdir -p build

build/quartz64b: build
	mkdir -p build/quartz64b

build/%.dtsp: %.dts
	cpp $(CPPFLAGS) $^ -o $@

build/%.dtbo: build/%.dtsp
	$(DTC) -O dtb -o $@ $(DTCFLAGS) $^

clean:
	rm -vfr build

.PHONY: clean install all

