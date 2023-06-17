# Profiling

## Within the framework

This (optional) phase allows to create profiles of the leakage that can be used
afterwards in the attack phase.
This profiling step can be implemented in the
`profile()` method of the `Attack` class in
[attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py).

It is defined as follows
```python
def profile(self, profile_datasets: List[DatasetReader]):
```
where `DatasetReader` is defined in
[dataset.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/dataset.py).
The function does not return anything, but **must set the value of the instance
variable `self.profile_model`** (which can be any `pickle`-able data).

The computation of the values manipulated by internal wires of the target may be
required during the profiling phase. While you can implement your
simulation procedure based on the
[SMAesH core architecture](https://github.com/simple-crypto/SMAesH), we provide
scripts to build a simulation library with Verime from the verilog code of the target (see
[Target simulation](./target_simulation.md)).  On the provided example attack, the
profiling phase consists in creating gaussian templates (together with a
reduction of dimensionality) for every shares of each bytes after the first
SubByte layer. For that, we directly use the SCALib
[LDAClassifier](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.modeling.LDAClassifier.html#scalib.modeling.LDAClassifier)
and rely on the [SNR](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.metrics.SNR.html) to select the POIs from the traces
(see [attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py) for more details).

To avoid re-computations, profiles are typically save to files using the
instance functions `save_profile()` and `load_profile()` (this is managed by
[quick_eval.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/quick_eval.py)).

When you submit a submission to the evaluation server, this profiling phase will be run.
There is a timeout of 4h for this run. If your profiling duration exceeeds that
limit, you can embed your profiles in the submission (see below).

## Outside the framework

You can also develop your own profiling methdology and save it results to a
file that you include in you submission package.
E.g., this approach should be used if your profiling is computationally
intensive, to the point of exceeding the limits set in the [rules](./rules.md).

When such a profile file is embedded into a submission package, the method to
follow for regenerating this file must be documented in the submission package (see
[Submission](./submission.md)).

Note that if you submission package exceeds 4 GB, it will not be accepted by
the evaluation server.
If this limit cannot be adhered to by your attack, we'd still like to be able
to accept it in the challenge. Please contact the organizers, we may (at our
discretion) arrange a way to bypass the 4 GB limit.

