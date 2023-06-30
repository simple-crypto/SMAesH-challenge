# Datasets

For each target, we have acquired 3 datasets:
- training dataset,
- validation dataset,
- test dataset.

The training and validation datasets are public, while the test dataset is used
to evaluate the submissions and kept private by the organizers.

All datasets correspond to a correct usage of the SMAesH core: for each trace,
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

The datasets have different levels of granularity in terms of data they contain. The 
following table summarizes which fields are provided with each datasets for all targets:

|      | Training / Validation (A7_d2) | Training / Validation (S6_d2) | Test |
| ---- | :----: | :----: | :----: |
| traces | &#x2611; | &#x2611; | &#x2611; |
| umsk_plaintext | &#x2611; | &#x2611; | &#x2611; |
| umsk_key | &#x2611; | &#x2611; | |
| msk_plaintext | &#x2611; | | |
| msk_key | &#x2611; | | |
| seed | &#x2611; | | |

Finally, the next table summarizes the global size of each dataset (in term of amount of traces).

| Dataset name | Target | Role | Number of traces | Length of traces |
| ---- | :----: | :----: | :----: | :----: |
| `SMAesH-A7_d2-vk0` | Artix-7 (\\( d = 2 \\)) | profiling | \\( 2 ^ {24} \\) | \\( 4250 \\) |
| `SMAesH-A7_d2-fk0` | Artix-7 (\\( d = 2 \\)) | validation | \\( 2 ^ {24} \\) | \\( 4250 \\) |
| `SMAesH-A7_d2-fk1` | Artix-7 (\\( d = 2 \\)) | test | \\( 2 ^ {24} \\) | \\( 4250 \\) |
| `SMAesH-S6_d2-vk0` | Spartan-6 (\\( d = 2 \\)) | profiling | \\( 2 ^ {24} \\) | \\( 4400 \\) |
| `SMAesH-S6_d2-fk0` | Spartan-6 (\\( d = 2 \\)) | validation | \\( 2 ^ {24} \\) | \\( 4400 \\) |
| `SMAesH-S6_d2-fk1` | Spartan-6 (\\( d = 2 \\)) | test | \\( 2 ^ {24} \\) | \\( 4400 \\) |

## Files organization and dataset reading

The dataset for the SMAesH challenge is
composed of several datasets, which are grouped by target and by security order
(denoted as a target isntance). For each target instance, we provide the training
and the validation dataset (respectively `vk0` and `fk0`), and keep private the test dataset (`fk1`).
Each dataset is
described by a manifest file (denoted `manifest.json`) that describes the
content of the dataset (including a file list and a way to check integrity) and
is composed of
several sub-directories (one per field stored in the dataset which is
containing the fields data).
The data files use the [NPY format](https://numpy.org/devdocs/reference/generated/numpy.lib.format.html).

The dataset are expected to be read with the tool
provided in `dataset.py` specifically implemented for this purpose. It
provides top level functions that allows to load the data contained in a
dataset per blocks of arbitrary size (see the definition of `iter_ntraces` in
`dataset.py` and its usage in `demo_submission/attack.py` for more details).

The architecture convention described above will be followed when the SMAesH
dataset will be extended with new target cases. The dataset organisation for the different targets 
are depicted by the following trees

```
smaesh-dataset/
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
+-- S6_d2/
| +-- vk0/
| | + manifest.json
| | +-- traces/
| | +-- umsk_plaintext/
| | +-- umsk_key/
| +-- fk0/
| | + manifest.json
| | +-- traces/
| | +-- umsk_plaintext/
| | +-- umsk_key/
```

See [here](./datasets_download.md) for download instructions.

### Hashes of datasets

SHA256 hashes of manifest files:
- `SMAesH-A7_d2-vk0`: `e067944fa0c630301c29f09cb53747bafd148af29032c87ff3a20a07e6401bc6`
- `SMAesH-A7_d2-fk0`: `91db2ed958c7c00e07eaec07cec8818e30c0dfd79cfcb8bac856db41f5b485b9`
- `SMAesH-A7_d2-fk1`: `08690d4152c2c6b979bd20cad489b5c99dafac7ad970fb60bcf91d67ea44be12`
- `SMAesH-S6_d2-vk0`: `6af82b2c13eec7de974f3ec25756c470910c4aeca612988bad7d5bcb39a74f7a`
- `SMAesH-S6_d2-fk0`: `fd0469d839336f0f7fe644c97949c1dfee9eb145011213b3ef29b4e334c5753b`
- `SMAesH-S6_d2-fk1`: `90f2b82fc3ec788523e90ef9682864dd3682179d7b5f19f8439a583cc87eb5fe`
