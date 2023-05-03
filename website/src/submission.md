# Submission

In this section, we explain how to prepare, package and test your submission,
before finally uploading it to the evaluation server.

At this point, we assume that your attack works with `quick_eval.py` (see [Framework](./framework.md)).


## Submission directory

Put your submission in a directory that satisfies the following (the
`demo_submission` directory is a good starting point).

1. It **must** contain the file`submission.toml`. See
   [demo_submission/submission.toml](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/submission.toml)
   for example and instructions.
1. If your attacks depend on python packages, put your dependencies in
   `setup/requirements.txt` (you can generate it with `pip freeze`).
1. It **must** contain the file `setup/setup.sh` with setup container
   instructions. If you only depend on python packages, keep the one of
   `demo_submission/`, otherwise, add your custom build/install steps here (see
   [Beyond Python](./not_python.md) for details).
1. Ensure that the ressources required by your submission are generated (e.g.,
   profile file, etc.). The demo submission is using a library (python wheel)
   built by verime. It should thus be generated (in `demo_submission/setup/`
   and must be listed in the file `demo_submission/setup/requirement.txt` for
   the evaluation to work. 
   To this end, the command
   ```bash
   # Run in venv-demo-eval environment.
   make -C demo_submission/values-simulations 
   ```
   generates the library wheel, copies it into the directory
   `demo_submission/setup` and updates the file
   `demo_submission/setup/requirements.txt` accordingly.
1. If your submission include non-source files (e.g., binary libraries or
   [profiled models](./profiling.md#outside-the-framework)), it must contain a
   succint README explaining how to re-generate those from source. It may also
   explain how your attack works.


## First test (in-place, native)

Test your submission with the `test_submission.py` script.
```bash
# To run in the SMAesH-challenge directory, assuming the submission directory is still demo_submission.
# To run after activating the venv-scripts virtual environment (see "Getting Started").
python3 scripts/test_submission.py --package ./demo_submission --package-inplace --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET
```

If this does not work, it is time to debug your submission. To accelerate the
debugging process, see the various command-line options of
`test_submission.py`. In particular, `--only` allows you to run only some steps
(e.g. `--only attack`).


## Building and validating the submission package

The
[scripts/build_submission.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/quick_eval.py)
scripts
generates a valid submission `.zip` file based on the submission directory. You can use the following command to generate
the package archive for the demo submission. 
```bash
# (To run in the venv-scripts environment.)
python3 scripts/build_submission.py --submission-dir ./demo_submission --package-file mysubmission.zip
```

Then, you can validate basic elements of its content with
```bash
python3 scripts/validate_submission.py mysubmission.zip
```

## Final tests

Let us now test the content of `mysubmission.zip`.
```bash
python3 scripts/test_submission.py --package mysubmission.zip --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET
```

If this succeeds, we can move to the final test. To ensure a reproducible
environment, submissions will be evaluated within a (docker-like) container
runtime.
The following test ensures that everything is functioning correctly inside the
container (and in particular that your submission has no un-listed native
dependencies -- the container is (before `setup.sh` runs) a fresh Ubuntu 23.04).
It will also validate resource constraints (you may want to relax timeouts if you
use a slower machine than the evaluation server).

- Install the [Apptainer](https://apptainer.org/) container runtime.
- Use `test_submission.py` in `--apptainer` mode:
```bash 
python3 scripts/test_submission.py --package mysubmission.zip --workdir workdir-eval-inplace --dataset-dir $SMAESH_DATASET --apptainer
```

If this works, congrats! The evaluation server uses the same command (albeit
with an additional `--attack-dataset-dir` argument), so you are ready to submit.you are ready to submit.you are ready to submit.you are ready to submit.

If it does not work, for debugging, note that the `apptainer` mode prints the
commands it runs, so you can see what happens.

You may want to:
- Use the `--package-inplace` mode of `test_submission.py` to avoid rebuilding the zip at every attempt.
- Run only some steps of the submission with the `--only` option.
- Clean up buggy state by deleting the `workdir`.
- Run commands inside the container using [`apptainer shell`](https://apptainer.org/docs/user/main/index.html).


## Upload

Create your team and upload your submission on the
[submission server](https://submit.smaesh-challenge.simple-crypto.org/). 
