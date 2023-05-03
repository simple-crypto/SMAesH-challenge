# Getting started

A dedicated evaluation framework has been developped for the challenge and is
available on [Github](https://github.com/simple-crypto/SMAesH-challenge). This
section explains the different steps that should be performed in order to run
the demo attack provided. More details about the evaluation framework can be
found in the dedicated [Framework](./framework.md) section.

## Installing dependencies

The framework runs with `python >= 3.8` and requires the following python tools:
- [`venv`](https://docs.python.org/3/library/venv.html), part of python's
  standard library, but not included by in some python installations
  (e.g., on ubuntu, you might have to `apt install python3-venv` to get it). 
- [`pip`](https://pip.pypa.io/en/stable/installation/), also, part of most
  python installations (but on ubuntu, `apt install python3-pip` is needed).

Additionally, the demonstration attack depends on
* [Yosys](https://yosyshq.net/yosys/) (version 0.25 tested, below 0.10 will likely not work)
* [Verilator](https://veripool.org/guide/latest/install.html#git-quick-install) (**use version 5.006**, many other version are known not to work)
* Make

**CAUTION**: we highly recommand to install Verilator from the
[git](https://github.com/verilator/verilator) and to run Verilator
[in-place](https://veripool.org/guide/latest/install.html#run-in-place-from-verilator-root) (as recommended by the official documentation).

We **highly recommend** to use the challenge in a unix environment (on windows,
use [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)).

## Cloning repo

First, clone the challenge framework repository:
```bash
git clone https://github.com/simple-crypto/SMAesH-challenge.git
```

## Downloading datasets

An archive containing the whole dataset is
[available](https://uclouvain-my.sharepoint.com/:u:/g/personal/charles_momin_uclouvain_be/Ee1uKH4DOzFCsUfdng3_CQMBuffb0RTspY39hR2kTlfc9Q?e=5WmfKv)
(~200Go, ~300Go uncompressed). It is compressed with the
[zstd](http://facebook.github.io/zstd/) tool, and archived in the `tar` format.

Individual files can be downloaded on our
[nextcloud](https://nextcloud.cism.ucl.ac.be/s/82XMewXRBP5PZNP)
server (see [Datasets](./datasets.md) for more info on the files content).

Next, we use the variable `SMAESH_DATASET` as the path to the directory where the
downloaded dataset is stored (i.e., the path to the directory `smaesh-dataset`,
which is the directory that contains the `A7_d2` directory). 

As a final step, format the dataset.
This operation must be done a single time on each fixed key dataset (it may last a few seconds).
This will generate a new manifest per dataset (`manifest_split.json`) that will be used by the framework's scripts to evaluate the attack.
```bash
# Create the venv for running framework's scripts
cd SMAesH-challenge
python3 -m venv venv-scripts
source venv-scripts/bin/activate # Activate it (adapt if not using bash shell)
pip install pip --upgrade 
pip install -r scripts/requirements.txt
# Run the split_dataset command
python3 scripts/split_dataset.py --dataset $SMAESH_DATASET/A7_d2/fk0/manifest.json 
# Leave de venv-scripts virtual environment
deactivate
```

## Running our example attack: profiling, attack, evaluation

The following steps allow to run the demo attack and to evaluate it.  

1. First, we move to the cloned framework directory
    ```bash
    cd SMAesH-challenge
    ```
1. Then, setup a python virtual environement used for the evaluation, and activate it
    ```bash
    python3 -m venv venv-demo-eval
    source venv-demo-eval/bin/activate
    pip install pip --upgrade 
    ```
1. Install the [verime](https://github.com/simple-crypto/verime) dependency (tool for simulating intermediate values in the masked circuit)
    ```bash
    pip install verime
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
1. Run the evaluation in itself 
    ```bash
    # Profiling step:
    # - uses the dataset vk0
    # - saves the templates in the current directory
    python3 quick_eval.py profile --profile-dataset $SMAESH_DATASET/A7_d2/vk0/manifest.json --attack-case A7_d2 --save-profile .
    
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
{59.79} \\).

By default, the profiling phase implemented uses \\( 2^{24}\\)
traces to build the models, which may result in a significant
processing time (it takes about 45 minutes on the [reference machine](./rules.html#evaluation-limits)).
The attack also runs in abouthe same time on that machine.
Reducing the number of traces for both steps will reduce their execution time
(at the expense of a worse key rank, of course).

*Note: you can run multiple steps at once, as in `python3 quick_eval.py profile attack eval ...`.*

## Next steps

It's your turn!

Both phases (profiling and attack) are implemented in the `profile()` and
`attack()` functions in
[attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py):
tweak these functions to implement your revolutionary attack.

If you get the demo submission to run with fewer traces, you can also try to directly [submit it](./submission.md)!

The other pages of this website provide more detailed information on how to
develop a submission. In particular: 

* [Framework](./framework.md) details how to use the framework of the challenge to develop, evaluate, package and send a new submission. 
* [Rules](./rules.md): see how to get points, and what are the constraints on submitted attacks.
* [Target](./targets.md): acquisition setup used for the different targets. 
* [Datasets](./datasets.md): content of the datasets.

Have a look at our [suggestions](./introduction.md#attack-ideas) and at the
[SMAesH documentation](https://simple-crypto.org/activities/smaesh) to get
ideas for improved attacks.

