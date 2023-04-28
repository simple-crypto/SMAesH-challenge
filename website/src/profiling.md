# Profiling

This (optional) phase allows to create profiles of the leakage (during an offline phase) that can be used
afterwards in the (online) attack phase. The variable key dataset is typically given to
this end. In order to implement the latter, a submission should implement the
`profile()` function of the `Attack` class (see file [attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py)). The later is defined as follows
```python
def profile(self, profile_datasets: List[DatasetReader]):
```
and takes as input a list of of `DatasetReader` (see
[dataset.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/dataset.py)).
The function does not return anything, but **must set the value of the instance
variable `self.profile_model`**.  Any data type can be used
to allow maximum genericity during the implementation. 

The computation of the values manipulated by internal wires of the target is
often required in such a profiling phase. While you can implement your
simulation procedure based on the
[SMAesH core architecture](https://github.com/simple-crypto/SMAesH), we rather
encourage to use an easy to use simulation library generated with Verime (see
[Target simulation](./target_simulation.md)).  On the provided example, the
profiling phase consists in creating gaussian templates (together with a
reduction of dimensionality) for every shares of each bytes after the first
SubByte layer. For that, we directly use the SCALib
[LDAClassifier](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.modeling.LDAClassifier.html#scalib.modeling.LDAClassifier)
and rely on the [SNR](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.metrics.SNR.html) to select the POIs from the traces
(see [attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py) for more details).

Depending on the use case, the user can choose to save the computed profile in
a file or not.  In that case, the instance functions `save_profile()` and
`load_profile()` will be used by the framework script [quick_eval.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/quick_eval.py). 
When a profile file is embedded into a submission, the method to follow for regenerating this file must be indicated in a README accompanying the submission (see [Submission](./submission.md)).
For the demo submission, the following command perfoms the profilling phase and stores the resulting model in a file
```
python3 quick_eval.py profile --profile-dataset $AESHPC_DATASET/A7_d2/vk0/manifest.json --attack-case A7_d2 --save-profile $SAVE_DIR
```
Here, `$AESHPC_DATASET` is the path to the directory where the downloaded
datasets are stored.  Moreover, the profile will be stored under the file
`$SAVE_DIR/profile.pkl` after the completion of the command.  Multiple values
can be given to the `--profile-dataset` parameter, to also use the fixed key
dataset in the profiling phase for instance. The helper of `quick_eval.py`
provides more information about the parameters that can be used.
