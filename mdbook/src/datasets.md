# Datasets

For each target, we have acquired 3 datasets:
- training dataset,
- validation dataset,
- test dataset.

The training and validation datasets are public, while the test dataset is used
to evaluate the submissions and kept private by the organizers.

All datasets correspond to a correct usage of the AES-HPC core: for each trace,
the sharing of the key and of the plaintext is fresh.  Moreover, we reseed the
core before each trace with a fresh seed (the reseeding is not included in the
trace).  In the training dataset we use a fresh random key and a fresh random
plaintext for each trace.  The validation and test datasets are sampled
identically and use a single fixed key (sampled at random) for the whole
dataset, and a fresh random plaintext for each trace.

## Dataset parameters

The dataset contains the power measurements collected with the evalutation setups described in [Targets](./targets.md)
together with some input data used for each execution of the AES-HPC core
execution. In particular, the following fields can be found: 

| Label | Type | Length | Description |
| ---- | :----: | :----: | ---- |
| traces | int16 | *ns* | power traces measurement of *ns* time samples. | 
| umsk_plaintext | uint8 | *16* | unshared plaintext. |
| umsk_key | uint8 | *16* | unshared key. |
| msk_plaintext | uint8 | *16* \\( \cdot \\) *d*| plaintext sharing with *d* shares. | 
| msk_key | uint8 | *16* \\( \cdot \\) *d* | key sharing with *d* shares. |
| seed | uint8 | *10* | PRNG seed of 80 bits.|
| | | | |

The datasets have different levels of granularity in terms of data they contain. For the Artix-7 target, the 
following Table summarizes which fields are provided with each datasets:

|      | Training / Validation | Test |
| ---- | :----: | :----: |
| traces | &#x2611; | &#x2611; |
| umsk_plaintext | &#x2611; | &#x2611; |
| umsk_key | &#x2611; | &#x2611; |
| msk_plaintext | &#x2611; | |
| msk_key | &#x2611; | |
| seed | &#x2611; | |

Finally, the next Table summarizes the global size of each traces (in term of amount of traces).

| Target | Dataset name | Training traces | Validation traces | Test traces | Length traces| 
| ---- | :----: | :----: | :----: | :----: | :----: |
| Artix-7 (\\( d = 2 \\)) | A7_d2 | \\( 2 ^ {24} \\) | \\( 2 ^ {24} \\) | \\( 2 ^ {24} \\) | \\( ns = 4250 \\) |


## Files organization and dataset reading

The datasets are available for download at TODO. They are organised per
target, according to the file tree represented below. In particular, only the datasets acquired
for the Artix7 target are currently available under `aes_hpc_datasets/A7_d2/.` 
Each target directory contains two sub-directories containing the
training set `vk0` and the validation set `fk0`. The value of the fields for each datasets are organised 
as file of \\( 2 ^ {24} \\) elements that are stored under dedicated subdirectories having the same name as the corresponding field.
```
aes_hpc_datasets/
+-- A7_d2/
| +-- vk0/
| | + manifest.json
| | +-- traces/
| | +-- umsk_plaintext/
| | +-- umsk_key/
| | +-- msk_plaintext/
| | +-- msk_key/
| | +-- seed/
| +-- fk0/
| | + manifest.json
| | +-- traces/
| | +-- umsk_plaintext/
| | +-- umsk_key/
| | +-- msk_plaintext/
| | +-- msk_key/
| | +-- seed/
```

Each dataset is described by a dedicated manifest `manifest.json` and is
expected to be read with the dedicated utility implemented in `dataset.py`.
Based on a manifest, the later provides top level functions that allows to read
data contained in a dataset per blocks of arbitrary size (see the usage of `iter_ntraces` in `dataset.py` and
`example_submission_package/attack.py` for more informations). 
