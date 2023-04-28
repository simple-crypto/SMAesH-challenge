# Attack

The attack phase is the only mandatory step that should be implemented in a submission. It consists 
in the practical implementation of the attack and can relies on a precomputed profile (see [Profiling](./modeling.md))
To this end, the function `attack` must be implemented in [attack.py](TODO). The later is defined as follows 
```python
def attack(self, attack_dataset: DatasetReader) -> KeyGuess
```
and takes as input a `DatasetReader` instance. In practice, the dataset reader
provided points to a fixed key dataset for which only the power measurements
and the value of the unmasked plaintext are provided (see
[Datasets](./datasets.md)). The goal of this function is to recover the value
of the 128-bit unmasked key used during the acquisition of the provided
dataset. The function must return a `KeyGuess` instance that will be used to
evaluate the performance of the attack. The later typically consists in a list
of probabilities associated to parts of the unmasked key following a divide-and-conquer strategy (see
[key_guess.py](TODO)). 

In the demo submission, we use the SASCA implementation from
[SCALib](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.attacks.FactorGraph.html)
to recover information about the 16 bytes of the key. The attack is not
optimised and does not achieve good performances, but is rather used
as a good starting point to ease the development of a new submission in the
evaluation framework (see [attack.py](TODO)). When a preliminar profiling
phase is required (as done in the demo submission), the computed/loaded profile
is stored in the variable `self.profiled_model` (the assignement of
this variable is handled by the framework script [quick_eval.py](TODO)). 

The following command is used to start the attack
```
python3 quick_eval.py attack --attack-dataset $AESHPC_DATASET/A7_d2/fk0/manifest.json --attack-case A7_d2 --load-profile $SAVE_DIR --save-guess $KGUESS_FILE_PATH --n-attack-traces $NT_ATCK
```
Here, `AESHPC_DATASET` is the path to the directory where the datasets are stored,
`KGUESS_FILE_PATH` is the path file where the `KeyGuess` instance returned by
the attack will be saved and `NT_ATCK` is the amount of traces to use for the
attack. If `--n-attack-traces` is not used then all the traces from the dataset
specified with `--attack-dataset` will be used. The parameter `--load-profile
SAVE_DIR` indicates to load the profile stored in the directory `SAVE_DIR` (it
is thus not required to execute unprofiled attacks). 

The framework also allows to perform both the profiling and the attack in a single execution (which saves the cost of storing the model on the disk). This is done 
by mixing parameters from the [Profiling](./profiling.md) and from the attack, as shown with the following example command
```
python quick_eval.py profile attack --profile-dataset $AESHPC_DATASET/A7_d2/vk0/manifest.json --attack-case A7_d2 --attack-dataset $AESHPC_DATASET/A7_d2/fk0/manifest.json --n-attack-traces $NT_ATCK --save-guess $KGUESS_FILE_PATH
```
