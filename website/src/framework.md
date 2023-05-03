# Framework

The [Getting Started](./getting_started.md) page explains in a minimal way
what are the commands to use in order to run the demonstration attack provided.
By following these, you can ensure that all the dependencies are properly
installed before starting implementing your own. 

In this section, we give more details on the challenge's python-based framework to develop
and evaluate attacks, available [on github](https://github.com/simple-crypto/SMAesH-challenge).
The following sections try
to guide a candidate through the implementation of a new submission. However,
not all the details are covered , and we invite the reader to refer to the
documentation found directly in the code for further explanation.

Next, we assume
that the attack is written in python, but the framework may also work with
other languages (see
[Beyond Python](not_python.md)).

## Contents
The framework is split in two parts:

- The code running the attack, given as a demonstration attack (`demo_submission` directory).
    This includes:
    * Loading the datasets.
    * Simulating internal states of the circuit.
    * Running a optional profiling step.
    * Executing the attack in itself.
    * Running a simplified evaluation for testing/developing purpose.
- The scripts (`scripts` directory) for
    * building a submission package,
    * checking that is it well-structured,
    * evaluating it.

## Dependencies

The main dependencies for the framework are given in
[Getting Started](./getting_started.md#installing-dependencies).

Additionally, the fully reproducible submission evaluation depends on
[Apptainer](https://apptainer.org/) (optional, see [Submission](./submission.md)).

## Usage

### Running attacks

There are multiple ways to an attack in the framework, that vary in their ease
of use, performance overheads and portability.

**Quick eval** Using the `quick_eval.py` python script in the submission is the
easiest. It also has minimal overhead, and it is therefore **ideal for
developping** an attack.
See [Getting Started](./getting_started.md) for usage instructions.

**Test submission** Since `quick_eval.py` is tightly integrated to a
submission, it is easy to use and modify, but this tight integration is not
always wanted: when evaluating a submission that is not our own, we would like
a more standard interface.
This is what the `scripts/test_submission.py` script provides. It has multiple
modes (attack in directory or zip file, native or containerized exeuction).
This shoud be mostly useful to **validate your submission package**.
See [Submission](./submission.md) for usage instructions.


### Implementing attacks

The implementation of an attack lies inside two python functions.

- The **profiling** function (optional), see [Profiling](./profiling.md).
- The **attack** function, see [Attack](./attack.md).

Do you need more flexibility? You can change anything in the `demo_submission`
directory, as long as the command-line interface remains the same.
See also [Beyond Python](./not_python.md).


### Submitting attacks

Once your attack works with `quick_eval.py`, see [Submission](./submission.md) for a
step-by-step list on how to send it to the evaluation server.

