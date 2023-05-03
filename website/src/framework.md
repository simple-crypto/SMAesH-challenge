# Framework
The Section [Getting Started](./getting_started.md) explains in a minimal way
what are the commands to use in order to run the demonstration attack provided.
By following these, you can ensure that all the dependencies are properly
installed before starting implementing your own. 

To this purpose, we provide a comprehensive python-based framework to develop
and evaluate attacks, available [on github](https://github.com/simple-crypto/SMAesH-challenge). The following sections try
to guide a candidate through the implementation of a new submission. However,
not all the details are covered , and we invite the reader to refer to the
documentation found directly in the code for further explanation.  Next, we assume
that the attack is written in python, but the framework may also work with
other languages (see
[Beyond Python](not_python.md)).

## Contents
The framework is split in two parts:

- The code running the attack, given as a demonstration attack.
    This includes:
    * Loading the datasets.
    * Simulating internal states of the circuit.
    * Running a optional profiling step.
    * Executing the attack in itself.
    * Running a simplified evaluation for testing/developing purpose.
- The scripts for building a submission package and evaluating it.

More particularly, the evaluation framework repository contains two
directories:
[demo_submission](https://github.com/simple-crypto/SMAesH-challenge/tree/main/demo_submission)
and
[scripts](https://github.com/simple-crypto/SMAesH-challenge/tree/main/scripts).
The files contained in `demo_submission` are all the files required to run the
implemented attack.  On the other hand, the files under `scripts` are scripts
that are dedicated to the evaluation of submissions. These are not strictly
necessary for the development of a new submission, but are rather provided to
offer the possibility to ensure that the latter is properly structured (and can pass the challenge evaluation).

## Dependencies

The framework runs with `python >= 3.8`. We suggest using python's standard
library virtual environment module `venv`. On some python installations, this
is not included by default (e.g., you have to `apt install python3-venv` to get
it). 

Additionally, the demonstration attack depends on
* [Yosys](https://yosyshq.net/yosys/) (Yosys 0.25 (git sha1 e02b7f64b, gcc 9.4.0-1ubuntu1~20.04.1 -fPIC -Os) tested)
* [Verilator](https://www.veripool.org/verilator/) (Verilator 5.006 2023-01-22 rev v5.006)
* Python (Python 3.10.6 tested)
* [Verime](https://pypi.org/project/verime/) (v1.0.1 tested)
* GNU Make (v4.2.1 Built for x86_64-pc-linux-gnu tested)
* [Apptainer](https://apptainer.org/) (optional, see [Evaluation](./evaluation.md))

## Getting started with the framework

The framework has been designed to limit a candidate's work to the
implementation of two functions (one being optional, the other being mandatory)
from a single file ([attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py), see [Profiling](profiling.md) and
[Attack](attack.md)). We provided tools dedicated to the reading of the dataset
(see [dataset.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/dataset.py) for more info and [attack.py](TODO) for example usage).
The [quick_eval.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/quick_eval.py) utility allows to execute the different sub-steps
necessary to validate the attack implementation. in particular, it allows to
execute the profiling, the attack itself and an evaluation of the latter. These
steps can be perfomed independantly or in a combined fashion. 

Next, we summarize the steps to follow in order to implement a new attack. We
also show how `quick_eval.py` can be used to run the demonstration
attack. We strongly encourage to develop your submission by tweaking this demo
attack (i.e., by modifying the `attack.py` file), as it significantly
reduces the amount of work required to integrate your submission in our evaluation
framework.

1. Download the datasets (see [Downloading
   dataset](getting_started.html#downloading-datasets)). We next assume that
   the macro `SMAESH_DATASET` holds the path to the directory storing
   downloaded dataset.
1. Clone the [challenge repository](https://github.com/simple-crypto/SMAesH-challenge). It is assumed next that the macro
   `SMAESH_FRAMEWORK` refers to the cloned repository.
1. From the challenge repository, perform the following steps to develop your attack:
    1. Create a virtual environment for development purpose
        ```bash
        python3 -m venv venv-demo-eval # Create the venv
        source venv-demo-eval/bin/activate # Activate it (using bash shell)
        pip install pip --upgrade 
        pip install verime # install Verime in the venv
        ```
        and don't forget to **activate it**.
    1. Go in the demo attack directory
        ```bash
        cd demo_submission
        ```
    1. Build the simulation library (for more details, see [Target Simulation](target_simulation.md)). 
        ```bash
        make -C values-simulations 
        ```
    1. Install the required dependencies.
        ```bash
        (cd setup && pip install -r requirements.txt)
        ```
    1. Format the dataset. This operation must be done a single time on each dataset (it may last a few seconds).
        This will generate a new manifest per dataset (denoted `manifest_split.json`) that will be used by the framework's scripts.
        ```bash
        python3 split_dataset.py --dataset $SMAESH_DATASET/A7_d2/vk0/manifest.json 
        python3 split_dataset.py --dataset $SMAESH_DATASET/A7_d2/fk0/manifest.json 
        ```
    1. Run the profiling phase (for more details, see [Profiling](profiling.md)):
        ```bash
        python3 quick_eval.py profile --profile-dataset $SMAESH_DATASET/A7_d2/vk0/manifest_split.json --attack-case A7_d2 --save-profile .
        ```
    1. Run the attack phase (for more details, see [Attack](attack.md)):
        ```bash
        python3 quick_eval.py attack --attack-dataset $SMAESH_DATASET/A7_d2/fk0/manifest_split.json --attack-case A7_d2 --load-profile . --save-guess ./keyguess-file --n-attack-traces 16777216
        ```
    1. Evaluate the attack (for more details, see [Evaluation](evaluation.md)):
        ```bash
        python3 quick_eval.py eval --load-guess ./keyguess-file --attack-case A7_d2 --attack-dataset $SMAESH_DATASET/A7_d2/fk0/manifest_split.json
        ```
1. Start tweaking the demo into your own super effective attack! In practice,
   it can be done by simply modifying the function `attack()` (and optionally
   `profile()`) in the file [attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py).
1. Once your happy with your attack performance, see [Submission](submission.md) for packaging your submission.

