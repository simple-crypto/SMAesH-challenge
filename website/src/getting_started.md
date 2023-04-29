# Getting started

A dedicated evaluation framework has been developped for the challenge and is
available on [Github](https://github.com/simple-crypto/SMAesH-challenge). This
section explains the different steps that should be performed in order to run
the demo attack provided. More details about the evaluation framework can be
found in the dedicated [Framework](./framework.md) section.

## Installing dependencies
The framework runs with `python >= 3.8`. We suggest using python's standard
library virtual environment module `venv`. On some python installations, this
is not included by default (e.g., you have to `apt install python3-venv` to get
it). 

Additionally, the demonstration attack depends on
* [Yosys](https://yosyshq.net/yosys/) (Yosys 0.25 (git sha1 e02b7f64b, gcc 9.4.0-1ubuntu1~20.04.1 -fPIC -Os) tested)
* [Verilator](https://www.veripool.org/verilator/) (Verilator 5.006 2023-01-22 rev v5.006)
* [Verime](https://pypi.org/project/verime/) (v1.0.0 tested)
* GNU Make (v4.2.1 Built for x86_64-pc-linux-gnu tested)
* [Apptainer](https://apptainer.org/) (optional, see [Running our example attack](./getting_started.html#running-our-example-attack-profiling-attack-evaluation))

## Cloning repos

Run the following commands to clone the challenge framework repository and set the macro. 
We denote next as `SMAESH_FRAMEWORK` the directory resulting from the clone
(i.e., the directory `DIR_CLONE/SMAESH-challenge`).
```bash
cd DIR_CLONE
git clone git@github.com/simple-crypto/SMAesH-challenge.git # Using SSH 
git clone https://github.com/simple-crypto/SMAesH-challenge.git # Using HTTPS
export SMAESH_FRAMEWORK=`pwd` # Set the MACRO
```

## Downloading datasets

An archive containing the whole dataset is [available](TODO) (~200Go, ~300Go
uncompressed).  The latter has been compressed with the
[Zstandard](http://facebook.github.io/zstd/) utility.  If only parts of the
dataset are to be downloaded, it is possible to select the files to be
downloaded via the
[Nextcloud](https://nextcloud.cism.ucl.ac.be/s/Q2WdNjXzsEtXoDa?path=%2Fsmaesh-challenge)
hosting service (see [Datasets](./datasets.md) for more info). 

Next, we use the macro `SMAESH_DATASET` as the path to the directory where the
downloaded dataset is stored (i.e., where the path of the directory `smaesh-dataset`). 

## Running our example attack: profiling, attack, evaluation
The following steps allow to run the demo attack and to evaluate it.  

1. First, we move to the cloned framework directory
    ```bash
    cd $SMAESH_FRAMEWORK
    ```
1. Then, setup a python virtual environement used for the evaluation, and activate it
    ```bash
    python3 -m venv venv-demo-eval # Create the venv
    source venv-demo-eval/bin/activate # Activate it (using bash shell)
    ```
1. In the demo submission directory, build the simulation library with Verime
    ```bash
    # First install Verime if required
    pip install pip --upgrade
    pip install verime # Install verime if required

    cd demo_submission
    make -C values-simulations 
    ```
1. Install the python package required
    ```bash
    pip install -r setup/requirements.txt
    ```
1. Run the evaluation in itself 
    ```bash
    # Computes the profile
    # - uses the dataset vk0
    # - saves the profile in the current directory
    python3 quick_eval.py profile --profile-dataset $AESHPC_DATASET/A7_d2/vk0/manifest.json --attack-case A7_d2 --save-profile .
    
    # Performs the attack using 16777215 traces 
    # - uses the dataset fk0
    # - loads the profile located into the current directory
    # - performs the attack using 524288 traces
    # - saves the keyguess resulting in the file './keyguess-file'
    python3 quick_eval.py attack --attack-dataset $AESHPC_DATASET/A7_d2/fk0/manifest.json --attack-case A7_d2 --load-profile . --save-guess ./keyguess-file --n-attack-traces 16777216

    # Evaluates the attack based on the result file produced
    # - loads the keyguess file generated with the attack
    # - use the key value of the dataset fk0 as a reference.
    python3 quick_eval.py eval --load-guess ./keyguess-file --attack-case A7_d2 --attack-dataset $AESHPC_DATASET/A7_d2/fk0/manifest.json
    ```
For the demo attack, the evaluation phase is expected to 
produce the following result on the standard output when the default configuration are used
```bash
...
log2 ranks [59.79907288]
number of successes 1
```
which means that the attacks reduces the rank of the correct key to \\( 2 ^
{59.79} \\). By default, the profiling phase implemented uses \\( 2^{24}\\)
traces to build the models, which may result in a significant amount of
processing time depending on your machine configuration. During development,
feel free to speed up the process (at the cost of weakening the attack) by
reducing the amount of traces used (during profiling and/or the attack phase).

Both phases (profiling and attack) are implemented using two dedicated
functions in
[attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py)
We advise to use the example submission as a basis for any new submission: a
new attack can easily be developped by tweaking the appropriate function. Try it yourself! 


