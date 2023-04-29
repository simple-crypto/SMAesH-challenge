# Submission

In this section, we explain how to properly package your submission before
uploading it to the challange submission server. 
At this point you are assumed to have already implemented your attack and
validated it (see the Profile, Attack and Evaluation sections).

From a global point of view, the following steps allow to generate a valid submission file.

1. Preparing the submission directory for the evaluation (see [Preparation of the submission](./submission.html#preparation-of-your-submission).
1. Evaluate the submission directory (optional, see [Submission Evaluation](./submission.html#submission-evaluation)).
1. Create the submission archive (see [Building the package archive](./submission.html#preparation-of-the-submssion.md])).
1. Evaluate the submission archive in a container environment (optional, see [Submission Evaluation](./submission.html#submission-evaluation)).
1. Upload your submission archive on the server.

The evaluation phases are not strictly necessary for the generation of the
submission archive. **However, we strongly advise you to carry them out** to ensure
that the evaluation of your attack candidate will run smoothly once submitted. 
The following commands performs the steps 1-4 for the demo submission. Please refer to the 
dedicated sections for further informations. 

```bash
# Move to the framework directory
cd $SMAESH_FRAMEWORK

# 1) Evaluate the submission directory
python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $AESHPC_DATASET

# 2) Generate the package archive
python3 scripts/build_submission.py --submission-dir demo_submission --package-file mysubmission.zip

# 3) Evaluate the submission archive
python3 scripts/test_submission.py --package ./mysubmission.zip  --workdir workdir-eval-zip --dataset-dir $AESHPC_DATASET

# 4) Evaluate the submission archive in a container
python3 scripts/test_submission.py --package ./mysubmission.zip  --workdir workdir-eval-zip --dataset-dir $AESHPC_DATASET --apptainer
```


## Preparation of your submission

To be valid, a submission must be developed in a single directory. The
structure of the latter is left to the choice of the applicants, but must
satisfy the following requirements

1. it **must** contain the file`submission.json` at the root (see [demo_submission/submission.json](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/submission.json) for an
   example). The latter is a JSON file configuring the submission. It must contain the following attributes
    1. `authors`: the list of authors. Organised as a list of entries, where each entry specifies an author. In particular, each entry **must** contain the name of the author (under the `name` attribute) and a valid email address (under the `email` attribute).
    1. `name`: the name of the submission package. 
    1. `license`: the license applying to the submission. Note that only open-source license (permissive or not) will be accepted. 
    1. `attacks`: the attack configuration claimed to be successful. Multiple targets can be configured (by putting multiple targets attributes) and each target **must** specifies a 
    claimed amount of attack traces for which the submitted attack is supposed to work. 
1. it **must** contain the file `setup/requirements.txt`. The latter **must**
   list all the python packages required (following the [pip file
   format](https://pip.pypa.io/en/stable/reference/requirements-file-format/))
   by the submission. 
1. it **must** contain the file `setup/setup.sh`. The latter is required to run
   the evaluation procedure in a container and is not expected to be modified
   for submission written only in Python (you can copy the one from the demo
   submission in that case). 
1. it may contain a succint README describing the submission package. The
   main role of the latter is to explain the steps required to reproduce some
   special feature of the submission, such as how to rebuild an embedded model
   file.  

## Submission Evaluation
As a sanity check, the framework provides a way to ensure that your submission
run as expected in the challenge evaluation framework. The script
[test_submission.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/scripts/test_submission.py) 
has been specially designed for this purpose. 
It allows the complete evaluation of a submission to be carried out in the same way as it will be done on the server.
The latter can be done at two levels during development: directly on the submission directory or on the package archive. 
The following commands show how to use [test_submission.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/scripts/test_submission.py) 
to perform the evaluation of your submission

1. Move the the cloned framework repository
    ```bash
        cd $SMAESH_FRAMEWORK
    ```
1. Create a Python virtual environment dedicated to the evaluation (it must be located outside your submission directory). Activate it and install the dependencies required by the 
evaluation procedure
    ```bash
    python3 -m venv venv-demo-eval
    source venv-demo-eval/bin/activate # Activation with bash shell
    pip install pip --upgrade
    pip install scripts/requirements.txt
    ```
1. Ensure that the ressources required by your submission are generated (e.g., profile file, ...). The demo submission is using a verime library. The latter should thus be generated and must be enlisted in the file `demo_submission/setup/requirement.txt` for the evaluation to work. 
To this end, the command
    ```bash
    make -C demo_submission/values-simulations 
    ```
    generates the library wheel, copies it into the directory
    `demo_submission/setup` and updates the file
    `demo_submission/setup/requirements.txt` accordingly. We encourage to
    explain the generation procedure of this kind of specificities instead of embedding large files in your submission. 
1. Execute the evaluation in itself. The evaluation of your submission can already be done prior to generating the submission zip file, which has the
    advantage of avoiding costly compression and decompression operations during
    the developement process. The different steps of the evaluation can be run independently or in an combined manner by running one (or several) of the following commands
    ```bash
    ## Run all the phases of the submission evaluation (in order, profiling, attack, evaluation)
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $AESHPC_DATASET
    
    ## Run the three phases independently
    # Profiling only 
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $AESHPC_DATASET --only profile
    # Attack only
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $AESHPC_DATASET --only attack
    # Evaluation only
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $AESHPC_DATASET --only eval
    # You can also combine different steps, e.g., attack and evaluation
    python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $AESHPC_DATASET --only attack eval
    ```
    The evaluation procedure starts by installing all the requirements specified in `demo_submission/setup/requirements.txt`. Then, the evaluation scripts act as a wrapper
    that execute command line calls to `demo_submission/quick_eval.py`.

To comply with the challenge's rules that limit resources during
evaluation, submissions will be evaluated within a container runtime. To ensure
that everything is functioning correctly inside the latter, `test_submission.py`
framework provides an option to verify it. For the demo submission, you can use the flag
--apptainer as shown next 
```bash 
python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $AESHPC_DATASET --apptainer
```
Initially, a dedicated Singularity container will be created for the submission. The latter is configured to run on Ubuntu 23.04
runtime. After the runtime setup is complete,
the script [setup/setup.sh](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/setup/setup.sh) from the submission will be called. This script can
is used to finalize the configuration of the runtime. It be modified to perform any necessary operations before proceeding to the
evaluation-specific operations (e.g., building the simulation library with verime).

As a final note, it is also possible to run the evaluation directly on a
package archive. In such case, the argument `--package` should indicates
archives's path and the flag `--package-inplace` should not be used anymore 

## Building the package archive

The utilitary
[scripts/build_submission.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/quick_eval.py)
generates a valid submission `.zip` file based on the submission directory. You can use the following command to generate
the package archive for the demo submission. 
```bash
python3 scripts/build_submission.py --submission-dir demo_submission --package-file mysubmission.zip
```
It generates the submission `mysubmission.zip` file. That can then be uploaded on the [submission server](TODO). 
