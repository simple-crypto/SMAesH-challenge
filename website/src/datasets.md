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
together with input data used at each execution of the core
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

The dataset for the SMAesH challenge is
composed of several datasets, which are grouped by target and by security order
(denoted as a target isntance). For each target instance, we provide a training
and a validation dataset (respectively `vk0` and `fk0`). Each dataset is
described by a manifest file (denoted `manifest.json`) and is composed of
several sub-directories (one per field stored in the dataset which is
containing the fields data). The dataset are expected to be read with the tool
provided in `dataset.py` specifically implemented for this purpose. It
provides top level functions that allows to load the data contained in a
dataset per blocks of arbitrary size (see the definition of `iter_ntraces` in
`dataset.py` and its usage in `demo_submission/attack.py` for more details).

The architecture convention described above will be followed when the SMAesH
dataset will be extended with new target cases. Currently, only the Artix7 case is available
and the dataset organisation is depicted by the following tree

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

See [here](./getting_started.md#downloading-datasets) for download instructions.
