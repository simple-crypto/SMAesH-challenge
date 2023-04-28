# Evaluation
In order to assess the quality of the implemented attack, the framework
provides an evaluation tool. In particular, based on the `KeyGuess` instance
produced, it computes an estimation of the rank of the correct key obtained
after the attack. In the context of the challenge, an attack is considered as successful
when the estimated rank resulting from it is below \\( 2 ^ {68} \\) (see
[Challenge rules](./rules.md)). The validation dataset is provided in order to
make it possible for a user to verify that its attack is working properly. For the demo submission, the command 
```
python3 quick_eval.py eval --load-guess $KGUESS_FILE_PATH --attack-case A7_d2 --attack-dataset $AESHPC_DATASET/A7_d2/fk0/manifest.json
```
allows to evaluate the `KeyGuess` instance saved in the file `KGUESS_FILE_PATH`
based on the correct fixed key from the validation dataset `fk0`.  The computed
rank estimation for the correct is key is plotted on the standard output.  It
has to be noted that the same methodology will be used to evaluate the
challenge submissions.  

As for the attack phase, it is possible to perform the evaluation step together
with the other steps in a single command. One may consider the following
command in order to execute the full flow
```
python quick_eval.py profile attack eval --profile-dataset $AESHPC_DATASET/A7_d2/vk0/manifest.json --attack-case A7_d2 --attack-dataset $AESHPC_DATASET/A7_d2/fk0/manifest.json --n-attack-traces $NT_ATCK
```
Please refer to the helper and the code of [quick_eval.py](TODO) to get more
information about the parameters that can be used.
