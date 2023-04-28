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

The following command can be used to easily run the demo attack and to evaluate
it.  These can be used to verify whether the submission package is behaving as
expected under the challenge evaluation procedure. 
1. First, we move to the cloned framework directory
    ```bash
    cd $SMAESH_FRAMEWORK
    ```
1. Then, setup a python virtual environement used for the evaluation, activate it
and install the dependencies required for the evaluation
    ```bash
    python3 -m venv venv-demo-eval # Create the venv
    source venv-demo-eval/bin/activate # Activate it (using bash shell)
    # Install python packages
    pip install pip --upgrade
    pip install scripts/requirements.txt
    ```
1. Build the simulation library used by the demo attack with Verime
    ```bash
    make -C demo_submission/values-simulations 
    ```
    For the demo submission, this command also updates the submission configuration (see [Submission](./submission.md) for more details).
1. Run the evaluation in itself (with some level of granularity)
    ```bash
    ## Run all the phases of the submission evaluation (in order, profiling, attack, evaluation)
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET
    
    ## Run the three phases independently
    # Profiling only 
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET --only profile
    # Attack only
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET --only attack
    # Evaluation only
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET --only eval
    # You can also combine different steps, e.g., attack and evaluation
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET --only attack eval
    ```
    By default, the demo attack uses \\( 2 ^ {24} \\) traces for the profiling
    phase and \\( 2 ^ {24} -1 \\) for the attack, which may result in a significant
    amount of processing time depending on your machine configuration. Feel free to speed up the 
    process (at the cost of weakening the attack) by reducing the amount of traces used, which can be done by editing the submission as follows
    
    * Set the value of `NT_PROF_SNR` and `NT_PROF_LDA` in `$SMAESH_FRAMEWORK/demo_submission/attack.py` to a low value, e.g., 16384. 
    * Set the value of `n_traces` in `$SMAESH_FRAMEWORK/demo_submission/submission.json` to a low value, e.g., 16384. 


For the demo attack, the evaluation phase is expected to 
produce the following result on the standard output when the default configuration are used
```bash
...
Amount of traces used in attack: 16777215
[112  26  97 156  98  87  57 183 186 128 212  99 179 122  74 250]
Attack on target A7_d2:
log2 ranks [59.79907288]
number of successes 1
```
which means that 
* 16777215 traces have been used during the online attack phase. The evaluation is directly using the amount of traces claimed by the submission (i.e., the attribute `n_traces` in `demo_submission/submission.json`, 
* the array of bytes depicts the value of the correct key (that should be recovered),
* the target evaluated was `A7_d2` (as configured in `demo_submission/submission.json`),
* the attacks reduces the rank of the correct key to \\( 2 ^ {59.79} \\),
* the evaluation results in 1 success taking into account the bound of \\( 2 ^ {68} \\) that should be reached to consider that an attack is successful (as detailled in [Challenge Rules](./rules.md)).

Optionally, the framework offers the possibility to evaluate a submission in a
isolated environment. In such that case, the evaluation will be performed inside a
Apptainer/Singularity container with a limited access to physical ressources
(as defined by the evaluation limits from [Challenge Rules](./rules.md)). This
can be done by adding the flag `--apptainer` at the end of every commands shown
above. As an example, the following command can be used to execute the full
evaluation flow in a container (provided that Apptainer is installed)
```bash
python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET --apptainer
```
**We strongly advise** to ensure that the containerized evaluation is behaving properly: 
the practical evaluation of canditates' submissions will be evaluated following the same procedure. 

## Making a submission

Once your happy with your attack implementation, you can create a submission
`.zip` file. Any submission is expected to contain a file `submission.json`
file that is used to configure the latter (e.g., select target and claimed amount of traces, specify authors, ...).  

For the example submission, the following command creates the submission package `$SMAESH_FRAMEWORK/mysubmission.zip` for the 
demo submission.  
```bash
python3 scripts/build_submission.py --submission-dir demo_submission --package-file mysubmission.zip
```
The latter can be uploaded on the submission server. 
**We however strongly advise** to validate that the submission `.zip` file has been correctly
generated. For this purpose, you can execute the evaluation phase directly on
the latter (see [Submission](./submission.md) for more details). As an example,
the following command performs the full evaluation inside a container for the
file `mysubmission.zip`
```
python3 scripts/test_submission.py --package ./mysubmission.zip --workdir workdir-eval-zip --dataset-dir $SMAESH_DATASET --apptainer
```
If the latter is working properly, you successfully generated a valid submission package that can be evaluated. Congrats! :)
