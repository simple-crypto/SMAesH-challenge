# Profiling

This (optional) phase allows to create profiles of the leakage that can be used
afterwards in the attack phase. The variable key dataset is typically given to
this end. In order to implement the latter, a submission must implement the
`profile()` function of the `Attack` class (see file [attack.py](TODO)). The later is defined as follows
```python
def profile(self, profile_datasets: List[DatasetReader]):
```
and takes as input a list of of `DatasetReader`. The function does not return
anything, but must set the value of the instance variable `self.profile_model`. 
The type of this variable is left to the user to allow maximum genericity
during the implementation. 

The computation of the values manipulated by internal wires of the target is
often required in such a profiling phase. While you can implement your
simulation procedure based on the
[AES-HPC](https://github.com/simple-crypto/aes_hpc) architecture, we rather
encourage to use an easy to use simulation library generated with Verime (see
[Target simulation](./target_simulation.md)).  On the provided example, the
profiling phase consists in creating gaussian template (together with a
reduction of dimensionality) for every shares of each bytes after the initial
key addition. For that, we directly use the SCALib
[LDAClassifier](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.modeling.LDAClassifier.html#scalib.modeling.LDAClassifier)
and rely on the [SNR](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.metrics.SNR.html) to select the POIs from the traces
(see the file [attack.py](TODO) for more details).

Depending on the use case, the user can choose to save the computed profile in
a file or not.  In that case, the instance functions `save_profile()` and
`load_profile()` will be used by the framework script [quick_eval.py](TODO)(the
user is not expected to use the later in any case). 
From the demo submission directory [TODO](TODO), the following command allows to
perfom the profilling phase and stores the resulting model in a file
```
python3 quick_eval.py profile --profile-dataset $AESHPC_DATASET/A7_d2/vk0/manifest.json --attack-case A7_d2 --save-profile SAVE_DIR
```
Here, `$AESHPC_FRAMEWORK` is the path to the directory where the downloaded datasets are stored.
Moreover, the profile will be stored under the file `SAVE_DIR/profile.pkl`
after the completion of the command.
Multiple values can be given to the `--profile-dataset` parameter, to also use
the fixed key dataset in the profiling phase for instance.
