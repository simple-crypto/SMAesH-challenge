# SMAesH Vivado project

## Structure
The SMAesH Verilog source files are located in 'aes_hdl'. These files are
annotated such that `keep_hierarchy` and `dont_touch` attribute are set for all
module instances. The wrapper around the target IP and to interface with the
controller MCU is located under `hdl`. 

The constraint file `cw305_main.xdc` is the acquisition setup constraint file.
The latter is deisgned to be intergrated in a CW305 board. Is has been used to
generate the bitstream of the acquisition setup. 

The script `vivado_project.tcl` is a TCL script that build the Vivado project
configured such that the optimisations are disabled. 

## How to rebuild the bitstream

Follow the next steps to regenerate the bitstream using the same configuration used
in the challenge:

1. Generate the Vivado project  
    ```bash
    vivado -mode batch -source vivado_project.tcl
    ```
    The Xilinx project file `cw305_ucg_target/cw305_ucg_target.xpr` should be generated.
1. Open the project using Vivado
1. Run the implementation flow (the toolflow parameters are already configured). 


