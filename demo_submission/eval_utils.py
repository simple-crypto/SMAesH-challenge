import key_guess
from dataset import DatasetReader
import msgpack
import msgpack_numpy

import numpy as np

msgpack_numpy.patch(allow_pickle=False)

MAX_SUCCESS_RANK = 2**64
MAX_SUBKEY_SIZE = 16

def load_kg(guess_path):
    with open(guess_path, 'rb') as f:
        kg = msgpack.load(f)
    return key_guess.KeyGuess.deserialize(kg)

def eval_attack(key_guess, attack_dataset_path):
    attack_dataset = DatasetReader.from_manifest(attack_dataset_path)
    assert key_guess.max_subkey_size() <= MAX_SUBKEY_SIZE
    key = [e['umsk_key'][0] for e in attack_dataset.iter_ntraces(1, fields=['umsk_key'])][0]
    ub = key_guess.key_rank_ub(np.unpackbits(key,bitorder='little').tolist())
    return ub
