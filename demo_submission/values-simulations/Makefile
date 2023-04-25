
PACK_NAME?=aeshpc_32bit_d${NSHARES}_lib
PACKAGE_DIR = $(abspath $(PACK_NAME))

AES_HPC_HDL_DIR = ./aes_enc128_32bits_hpc2

VERILOG_TOP = ${AES_HPC_HDL_DIR}/aes_enc128_32bits_hpc2.v
NSHARES=2

VERILOG_PARAMS = d=$(NSHARES)
VERILOG_SRC_DIRS = \
	    ${AES_HPC_HDL_DIR} \
	    ${AES_HPC_HDL_DIR}/masked_gadgets \
	    ${AES_HPC_HDL_DIR}/rnd_gen \
	    ${AES_HPC_HDL_DIR}/sbox 

SIMU_FILE = simu_aeshpc_32bit.cpp

REQU_FILE = ../setup/requirements.txt 

all: verime upd-setup

verime:
	verime \
	    $(addprefix -y ,$(VERILOG_SRC_DIRS)) \
	    -g $(VERILOG_PARAMS) \
	    --top $(VERILOG_TOP) \
	    --pack $(PACK_NAME) \
	    --build-dir $(PACKAGE_DIR) \
	    --simu $(SIMU_FILE)
	make -C $(PACKAGE_DIR)

upd-setup:
	echo $(notdir $(shell find $(PACKAGE_DIR) -name '*.whl'))
	sed -i '1 s/.*/$(notdir $(shell find $(PACKAGE_DIR) -name '*.whl'))/' $(REQU_FILE)
	cp $(shell find $(PACKAGE_DIR) -name '*.whl') ../setup



clean:
	rm -rf $(PACKAGE_DIR)

.PHONY: verime clean all

