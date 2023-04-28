# Target simulation

In order to analyse the circuit, it is necessary to know the internal values it
handles. To this end, our strategy is to simulate the behaviour of the circuit
and to recover the values that interest us. This solution avoids the need to
write specific code for each targeted signal (which is time consuming and can
lead to errors). We propose to use the simulation tool Verilator, which has
proven to be very efficient for behavioural simulations. To this end, the
Verime utility has been specifically developed to facilitate the integration of
Verilator into a Python-based toolflow. In particular, it acts as a wrapper
that automatically generates the files needed to compile with Verilator and
generates a python package that allows a user to easily simulate a circuit and
retrieve the signal values he wants. In this section we only explain how Verime
is used in the example framework and try to follow the same structure as Verime
documentation example. 

## Identification of useful signals 
As a basic example, we consider that an adversary wants to perform a template
attack against our AES-HPC implementation. To this end, he seeks to model the
power consumption of the implementation as a function of the share values
manipulated after the first key addition (i.e., the bytes of the state entering
the first layer of Sboxes). 

As explained in detailed in the [AES-HPC
documentation](https://github.com/simple-crypto/aes_hpc), these values are
manipulated by the core at the beginning of the execution. More particularly,
the wires `sh_4bytes_toSB` coming from the state datapath hold the target values when
`cnt_cycles` equals to 1, 2, 3 and 4 in Figure 16. The adversary has
thus to recover the values passing on these wires at these specific clock
cycles in order to be able to build his templates.

## Verilog annotation for Verime
The first step to do is to annotate the HDL of the architecture with the
`verilator_me` attribute in order to drive the operations performed by Verime.
This annotation is necessary in order to designate the signals from which we
wish to obtain the value. 

Targeting the AES-HPC module, this can be achieved by adding the
`verilator_me` attribute on the `state_sh_4bytes_to_SB` signal in the the
source file
[MSKaes_32bits_core.v](https://github.com/simple-crypto/aes_hpc/blob/main/hdl/aes_enc128_32bits_hpc2/MSKaes_32bits_core.v)
(as shown next)

```verilog
...
(* verilator_me = "b32_fromAK" *)
wire [32*d-1:0] state_sh_4bytes_to_SB;
...

```
The value of the wire `state_sh_4bytes_to_SB` will then be accessible through
the label `b32_fromAK`. Multiple internal values can be annotated with the
`verilator_me` attribute, but the labels used for each signals has to be
different. In addition to wires, ports, registers and/or array of wire and registers
can be annotated as well (please refer to the Verime documentation for more
details).  

## Implementation of the C++ simulation wrapper
The next step is to implement the top-level interface of the simulated HW
module. The goal of the later is to define how the HW module is used during a single execution.
In particular, the user has to implement the function `run_simu` with the following definition
```c
void run_simu(
        SimModel *sm,
        Prober *p,
        char* data,
        size_t data_size
        )
```
where the structures `SimModel` and `Prober` are specific to Verime (accessible
by using the statement `#include "verime_lib.h"`), `data` is the input data for
a single execution (encoded as an array of bytes) and `data_size` the amount of
bytes provided.  As explained in details in the Verime documentation, the
Verilated instance of the HW module can be accessed under the variable
`sm->vtop`, which allows the access/set the value of any signal at the
top-level.  In addition to the features enabled by Verilator, Verime implements
the two following additional functions under `verime_lib.h`

* `sim_clock_cycle(SimModel * sm)`: simulates a posedge clock cycle.
* `save_state(Prober * p)`: saves the values of the probed signals (i.e., the
one that are annoted with `verilator_me`).

The file [simu_aeshpc_32bit.cpp](TODO) implements a simple wrapper that stores
the values of the probed signals at every clock cycle once an execution
started. Next, we detail each part of the file. First, the verime library is
included and the value of the generic `d` that is considered is fetch
```c
#include "verime_lib.h"

#ifndef D
#define D GENERIC_D
#endif
...
```
It has to be noted that the value of every generic that will be used during the
Verime process can be accessed in the C++ wrapper by refering to the macro
`GENERIC_$(capital_generic_name)`. Then, we the function `run_simu` is implemented.   
We start the later by applying a reset of the core as follows
```c
...
// Reset the AES core
sm->vtop->rst = 1;
sim_clock_cycle(sm);
sm->vtop->rst = 0;
sim_clock_cycle(sm);
...
```
These four lines simply assert the reset control signal of the AES-HPC core
during a single clock cycle and then deassert it during another clock cycle.
Then, we implement procedure of the module is performed by performing an input transaction at the 
randomness interface of the AES-HPC core. In practice the following lines are used
```c
...
// Feed the seed
memcpy(&sm->vtop->in_seed,data,SEED_PRNG_BYTES);
sm->vtop->in_seed_valid = 1;
sm->vtop->eval();

while(sm->vtop->in_seed_ready!=1){
    sim_clock_cycle(sm);
}
sim_clock_cycle(sm);
sm->vtop->in_seed_valid = 0;
...
``` 
and the later naively implements the transaction. More into the details, the
seed is copied from the data buffer to the dedicated bus at the AES-HPC
top-level. Then, the control signal `in_seed_valid` is asserted and clock cycles are simulated 
until the signal `in_seed_ready` is also asserted. When exiting the while loop, an additional clock cycle
is simulated in order to complete the transaction. Once done, `in_seed_valid` is deasserted. 
The call to `eval()` is used to recompute the internal values resulting from combinatorial logic. 
The next step consists in starting the execution using the provided plaintexts and key, which is achieved by 
the following piece of code
```c
...
// Prepare the run with input data
// Assign the plaintext sharing
memcpy(&sm->vtop->in_shares_plaintext,data+SEED_PRNG_BYTES,16*D); 
// Assign the key sharing 
memcpy(&sm->vtop->in_shares_key,data+SEED_PRNG_BYTES+16*D,16*D);

// Start the run
sm->vtop->in_valid = 1;
sm->vtop->eval();
while(sm->vtop->in_ready!=1){
    sim_clock_cycle(sm);
}
sim_clock_cycle(sm);
sm->vtop->in_valid = 0;
sm->vtop->eval();
...
```
This step starts by copying the plaintext and key sharing from the data to the input bus. Then, it implements a transaction on the input interface by asserting
`in_valid`  and wait that `in_ready` is also asserted. Finally, we wait until the completion of the execution by simulating a clock cycle until the signal `out_valid` is 
asserted. While waiting, the probed signals are saved at every clock cycle by calling `save_state(p)` as shown here

```c
...
// Run until the end of the computation
while(sm->vtop->out_valid!=1){
    save_state(p);
    sim_clock_cycle(sm);    
}
save_state(p);
...
```
## Building of the python3 simulation package
The simulation package can be built provinding an annotated design and the corresponding simulation wrapper.
The building process is done in two simple steps:

1. Generating the package files using Verime.
1. Building the python package using the Makefile generated by Verime. 

The [Makefile](TODO) combines both steps in the target `verime` and it suffices
to use the later to create the python3 package (the following explanation
detail what it does in practice). Basically, the first step consists in using
Verime with the appropriate arguments in order to setup the package. The tool
will analyze the hardware architecture, identify the annoted signals and create
C++ files in order to probe these signals with Verilator (i.e., it will
generate the `verime_lib.*` files). Besides, it will generate all the python
environment used in the wheel building process.  As shown by ts helper, Verime
accepts the following parameters:

```bash
  -h, --help            show this help message and exit
  -y YDIR [YDIR ...], --ydir YDIR [YDIR ...]
                        Directory for the module search. (default: [])
  -g GENERICS [GENERICS ...], --generics GENERICS [GENERICS ...]
                        Verilog generic value, as -g<Id>=<Value>. (default: None)
  -t TOP, --top TOP     Path to the top module file, e.g. /home/user/top.v. (default: None)
  --yosys-exec YOSYS_EXEC
                        Yosys executable. (default: yosys)
  --pack PACK           The Verilator-me package name. (default: None)
  --simu SIMU           Path to the C++ file defining run_simu (default: None)
  --build-dir BUILD_DIR
                        The build directory. (default: .)
  --clock CLOCK         The clock signal to use. (default: clk)
```

In practice, the [Makefile]() calls Verime with the following arguments under the target `verime`:

* `--ydir ./aes_hpc/hdl/aes_enc128_32bits_hpc2 ./aes_hpc/hdl/aes_enc128_32bits_hpc2/masked_gadgets ./aes_hpc/hdl/aes_enc128_32bits_hpc2/rnd_gen ./aes_hpc/hdl/aes_enc128_32bits_hpc2/sbox`: used to point to the directories in which the AES-HPC source files are located. 
* `-g d=2`: set the value of the generic `d` at the top-level of the AES-HPC
* `--top ./aes_hpc/hdl/aes_enc128_32bits_hpc2/aes_enc128_32bits_hpc2.v`: specify the top module path.
* `--pack aeshpc_new_32bit_d2_lib`: define the package name. 
* `--build-dir aeshpc_new_32bit_d2_lib`: uses to indicates the directory used for the building process (in practice, a directory with the package name in the current directory).
* `--simu TODO`: indicates the path to the [simu_aeshpc_32bit.cpp](TODO) file.

After the Verime execution, the directory defined with `--build-dir` contains a
automatically generated Makefile. The latter first uses Verilator in order to
build a shared library. The later will then be used as an efficient backend
simulator. Finally, the python package is generated and the wheel
`aeshpc_new_32bit_d2_lib/aeshpc_light_32bit_d2_lib-*.whl` is created. 
The following section explain how the provided example integrates the later. 


## Basic usage of the simulation package.

Once installed, the generated simulation package can be used to easily probe
the annotated signal. It is considered next that the wheel generated in the
previous step has been installed in the python environment. The following piece
of code shows how to use the generated package
```python
import aeshpc_new_32bit_d2_lib as pred
import numpy as np

### Generate random input data byte.
# Amount of cases to simulate
n_cases = 100
# Amount of input byte for a single case
len_data = 10 + pred.GENERICS['d']*16 + pred.GENERICS['d']*16
# Random input byte
data_bytes = np.random.randint([n_cases, len_data],dtype=np.uint8)

### Simulate the cases
# Amount of probed state to allocate 
# (>= number of calls to save_state() in the C++ wrapper)
am_probed_state = 110
simulations_results = pred.Simul(
        cases,
        am_probed_state
        )

### Recover the data for a specific cycle  
# Value of the state recover for all simulated cases
sh_4bytes_toSB_clk1 = simulations_results["b32_fromAK"][:,1,:]
sh_4bytes_toSB_clk2 = simulations_results["b32_fromAK"][:,2,:]
sh_4bytes_toSB_clk3 = simulations_results["b32_fromAK"][:,3,:]
sh_4bytes_toSB_clk4 = simulations_results["b32_fromAK"][:,4,:]
```
The first lines are generating the numpy 2D-array `data_bytes` with random
bytes. Each row of this array contains the input bytes of a single simulation
case. In practice, each of these rows corresponds to an array `char * data`
that will be used by the function `run_simu()` in the simulation wrapper. In
this example, 100 independant random cases are generated, and each row contains
the bytes representing the \\( 80 \\)-bits seed, the \\( 128 d \\)-bits
plaintext and key. Note that the practical amount of the amount of share \\( d
\\) is fetch from the value that has been passed to Verime during the building
process by accessing to the `GENERICS` metadata of the package.  

Next, we use the package to simulate all the input cases. To this end, the package function `Simul()` takes two input parameters:
the cases input data (as a numpy array of bytes with a shape of (n_cases, len_data)) and the amount of probed state to allocate. 
More into the detail, the backend will allocate memory in order to store a given amount of times each annotated signal per case. 
Each time the function `save_state()` is called, the value of the annoted signals are stored to the buffer. In our present example, the saving 
is done at every clock cycle, and a total of 106 saves is done for a single execution. 

The results of the simulation for each cases are stored in the variable
`simulations_results`. In particular, the values of a specific annotated signal
can be accessed directly using the label used in the `verilator_me` attribute.
The simulation results for a specific signal is presented as a 3D bytes array
of dimension (`n_cases`, `am_probed_state`, `bytes_len_sig`), with

* `n_cases`: the amount of simulated cases.
* `am_probed_state`: used for the memory allocation of the simulation.
  Correspond to the maximum amount of time `save_state()` can be called in the
  simulation wrapper. In particular, using the index *i* at the second dimension allows to recover the 
  value of the *i*-th call to `save_state()` perfomed in the simulation wrapper. 
* `bytes_len_sig`: the amount of bytes required to encode the simulated signal. 

It results that the variables `sh_4bytes_toSB_clk1`, `sh_4bytes_toSB_clk2`,
`sh_4bytes_toSB_clk3` and `sh_4bytes_toSB_clk4` hold the targeted values 
(i.e., the values of the wires `sh_4bytes_toSB` for the clock indexes 1, 2, 3 and 4)
when the input vectors stored in `data_bytes` are used at the input of the
core. 

### Integration in the example submission package 
To ease the readibility of the model/attack scripts provided, thefile
[tap_config.py](TODO) defines the `TapSignal` class that allows to define a
specific signal of interest and provides useful features to easily deal with
the simulated values. In particular, each instance implements the simulation
feature of the configured signal. Besides, it offers additional feature that
are useful when the configured tapped internal bus holds a sharing (i.e., a
masked value). In particular, the user can select to recover a specific sharing
or the unmasked value hold by the wire. In practice, the following parameters
must be provided to each TapSignal instance

| Instance parameter | Type | Description |
| ---- | :----: | ---- |
| `sig_name` | str | Verime label of the annotated signal | 
| `cycle` | int | Clock index of interest (considering that the values of the annotated signals are saved at each clock cycle).|
| `share_index` | obj | Share index to tap. The user has the choice between<ul><li>`'raw'`: The raw value of the bus.</li><li>`None`: The unmasked/recombined value of the bus.</li><li>\\( i \leq d \\): the share index \\( i \\). In that case, only the value of the \\( i \\)-th share will be recover by the simulation.</li></ul> |
| `tap_bits` | list of integers or range | The bits indexes of interest. The behaviour depends on the value of `share_index`<ul><li>`'raw'`: the indexes represent bits indexes in the raw internal bus.</li><li>`None`: indexes represent bits indexes of the unshared value.</li><li>\\( i \\): indexes represent bits indexes of the configured share.</li></ul> |
| `am_shares` | int | Amount of shares used the encode the shared value. | 

In practice, a `TapSignal` instance is generated for each shares of each bytes
of the state after the first key addition of the AES execution (as done per the
function `generate_TC_from_AK()` in [tap_config.py](TODO)). The tap signal are
then used in the profilling phase in order to recover the traces label when
building the templates. As a final remark, the `TapConfig` class has been
designed in order to ease the management of multiple `TapSignal` instances.

