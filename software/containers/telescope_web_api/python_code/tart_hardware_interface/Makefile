develop: venv
	$(VENV)/python setup.py develop

test:	
	export CONFIG_DIR=../../config_data; $(VENV)/python test/testbench.py

dist:
	cp ../../../hardware/FPGA/tart_spi/data/permute.txt tart_hardware_interface/permute.txt
	python3 setup.py sdist
	
test_upload: dist
	twine upload --repository testpypi dist/*

upload: dist
	twine upload --repository pypi dist/*

.PHONY: test

include Makefile.venv
