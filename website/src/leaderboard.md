
# Leaderboard


This pages lists the attacks against the SMAesh dataset.


## CHES2023 challenge

These attacks were submitted for the [CHES2023 challenge](https://ches.iacr.org/2023/challenge.php) and follow the [challenge rules](./rules.md).

| Target | Authors | Attack | Traces |
| :----: | ------- | ------ | :----: |
| `A7_d2` | Gaëtan Cassiers, Charles Momin | [Demo](https://github.com/simple-crypto/SMAesh-challenge) | 16777215 |
| `A7_d2` | Thomas Marquet | Morningstar-1 | 6500000 |
| `A7_d2` | Thomas Marquet | Morningstar-1.3 | 5000000 |
| `A7_d2` | Valence Cristiani | Angelo | 500000 |
| `A7_d2` | Valence Cristiani | Raphaellio | 390000 |
| `A7_d2` | Valence Cristiani | Donatella | 290000 |
| `S6_d2` | Valence Cristiani | Leonardddo | 10000000 |
| `S6_d2` | Valence Cristiani | Leonardda | 5000000 |
| `S6_d2` | Thomas Marquet | Morningstar-2.2-try-again | 2150400 |
| `S6_d2` | Thomas Marquet | Morningstar-2.5 | 1638400 |
| `S6_d2` | Thomas Marquet | Morningstar-2.5.2 | 1228800 |
| `S6_d2` | Thomas Marquet | Morningstar-xxx | 901120 |

These attacks can be downloaded [here](https://github.com/simple-crypto/SMAesH-challenge-submissions).

## Post-CHES challenge

After the CHES challenge, the test datasets have been released (as well as the profiling randomness for the `S6_d2` dataset).

We invite everybody who works with the dataset to report their attacks to [the challenge organizers](mailto:info@simple-crypto.dev) (paper and/or code link). We aim to maintain here a list of all public attacks on the dataset.
Ideally, attack code should work within the [evaluation framework](./framework.md), in order to ease reproduction.

### Following challenge rules

To qualify, an attack should have been trained only on the training and validation datasets, and evaluated on a test dataset (taking the first \\(x\\) traces of that dataset).

| Target | Authors | Attack | Traces | Use prof. RNG seed |
| :----: | ------- | ------ | :----: | :----------------: |

### Other attacks

We list here the attacks that we are aware of, but that do not follow the challenge rules.

- (None at the moment.)
