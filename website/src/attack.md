# Attack

The attack phase is the only mandatory step that should be implemented in a submission. It
takes as input a set of traces and computes a subkey scores.
It can also use [Profiling](./profiling.md) data.

To this end, the method `attack` must be implemented in
[attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py):
```python
def attack(self, attack_dataset: DatasetReader) -> KeyGuess
```
where `DatasetReader` is defined in
[dataset.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/dataset.py)
and `KeyGuess` is defined in
[key_guess.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/key_guess.py)). 
When a profiling phase is used (as done in the demo submission),
the computed/loaded profile is stored in the variable `self.profiled_model`
(the assignement of this variable is handled by `quick_eval.py`). 

The dataset reader points to a fixed key dataset that contains only the power
traces and the unmasked plaintext (see [Datasets](./datasets.md)).

The `KeyGuess` consists in a split of the 128-bit key in subkeys (of at most 16
bits, which can be non-contiguous), and, for each subkey, a list that gives a
score for each of its possible values.
The score of a key value is the sum of the scores of its subkeys, and it determines the rank.
See also the [documentation of `KeyGuess`](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/key_guess.py). 

In the demo submission, we use the SASCA implementation from
[SCALib](https://scalib.readthedocs.io/en/stable/source/_generated/scalib.attacks.FactorGraph.html)
to recover information about the 16 bytes of the key. While it works (as shown
in [Getting Started](./getting_started.md)), the attack is not optimised and
does not achieve good performance, but it is a starting point for the
development of better attacks within our evaluation framework (see
[attack.py](https://github.com/simple-crypto/SMAesH-challenge/blob/main/demo_submission/attack.py)).

