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
* [Verilator](https://veripool.org/guide/latest/install.html#git-quick-install) (Verilator 5.006 2023-01-22 rev v5.006)
* [Verime](https://pypi.org/project/verime/) (v1.0.1 tested)
* GNU Make (v4.2.1 Built for x86_64-pc-linux-gnu tested)
* [Apptainer](https://apptainer.org/) (optional, see [Running our example attack](./getting_started.html#running-our-example-attack-profiling-attack-evaluation))

**CAUTION**: we highly recommand to install Verilator from the
[git](https://github.com/verilator/verilator) and to run Verilator
[in-place](https://veripool.org/guide/latest/install.html#run-in-place-from-verilator-root) (as recommended by the official documentation).

## Cloning repos

Run the following commands to clone the challenge framework repository and set the macro. 
We denote next as `SMAESH_FRAMEWORK` the directory resulting from the clone
(i.e., the directory `DIR_CLONE/SMAesH-challenge`).
```bash
git clone git@github.com/simple-crypto/SMAesH-challenge.git # Using SSH 
git clone https://github.com/simple-crypto/SMAesH-challenge.git # Using HTTPS
cd SMAesH-challenge 
export SMAESH_FRAMEWORK=`pwd` # Set the MACRO
```

## Downloading datasets

An archive containing the whole dataset is
[available](https://uclouvain-my.sharepoint.com/:u:/g/personal/charles_momin_uclouvain_be/Ee1uKH4DOzFCsUfdng3_CQMBuffb0RTspY39hR2kTlfc9Q?e=5WmfKv)
(~200Go, ~300Go uncompressed).  The latter has been compressed with the
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
    pip install pip --upgrade 
    pip install verime # install Verime in the venv
    ```
1. In the demo submission directory, build the simulation library with Verime
    ```bash
    cd demo_submission
    make -C values-simulations 
    ```
1. Install the python package required to run the attack
    ```bash
    (cd setup && pip install -r requirements.txt)
    ```
1. Format the dataset. This operation must be done a single time on each dataset (it may last a few seconds).
    This will generate a new manifest per dataset (denoted `manifest_split.json`) that will be used by the framework's scripts.
    ```bash
    python3 split_dataset.py --dataset $SMAESH_DATASET/A7_d2/vk0/manifest.json 
    python3 split_dataset.py --dataset $SMAESH_DATASET/A7_d2/fk0/manifest.json 
    ```
1. Run the evaluation in itself 
    ```bash
    # Computes the profile
    # - uses the dataset vk0
    # - saves the profile in the current directory
    python3 quick_eval.py profile --profile-dataset $SMAESH_DATASET/A7_d2/vk0/manifest_split.json --attack-case A7_d2 --save-profile .
    
    # Performs the attack using 16777215 traces 
    # - uses the dataset fk0
    # - loads the profile located into the current directory
    # - performs the attack using 524288 traces
    # - saves the keyguess resulting in the file './keyguess-file'
    python3 quick_eval.py attack --attack-dataset $SMAESH_DATASET/A7_d2/fk0/manifest_split.json --attack-case A7_d2 --load-profile . --save-guess ./keyguess-file --n-attack-traces 16777216

    # Evaluates the attack based on the result file produced
    # - loads the keyguess file generated with the attack
    # - use the key value of the dataset fk0 as a reference.
    python3 quick_eval.py eval --load-guess ./keyguess-file --attack-case A7_d2 --attack-dataset $SMAESH_DATASET/A7_d2/fk0/manifest_split.json
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

If necessary, the other sections provide more detailed information on how to
develop a submission. In particular: 

* [Target](./targets.md) details the acquisition setup used for the different
  targets. 
* [Datasets](./datasets.md) details the architecture of the dataset.
* [Framework](./framework.md) details how to use the framework of the challenge to develop, evaluate and package a new submission. 

