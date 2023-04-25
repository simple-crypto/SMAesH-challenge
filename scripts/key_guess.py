
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from typing import List

import scalib.postprocessing

@dataclass
class KeyGuess:
    """Description of a 'divide-and-conquer' key guess.

    A key is a sequence of nbits bits indexed from 0 to nbits-1,
    which are grouped in subkeys. Each subkey is a sequence of bit
    indices such that the parts form a partition of {0,...,nbits-1}.

    E.g., considering a byte-based attack on AES128, nbits=128 and
    subkeys = [[0,1,..,7], [8,...,15], ..., [120,...,127]].

    Each subkey has a value, that is, let the key
    be [k_0, k_1, ..., k_{nbits-1}] and a subkey have the indices
    ski = [s_0, ..., s_{n-1}], the value of the subkey is
    skv = [k_{s_0}, ..., k_{s_{n-1}}], or, equivalently
    skv' = \sum_{i=0}^{n-1} 2^i k_{s_i}.
    The values of all the subkeys uniquely determines the value of the key.

    E.g., the subkey values can be the values of the bytes of an AES128 key.

    In a key guess, we associate a score to each value of a subkey:
    subkey_scores = [score_{skv'=0}, ..., score_{skv'=2^n-1}].
    The score of a key is the sum of the scores of its subkey, and the rank of
    a key is the number of keys with a lower score (including itself).
    """
    subkey_indices: List[List[int]]
    scores: List[npt.NDArray[np.float64]]
    nbits: int

    def __init__(self, subkey_indices, scores, nbits=128):
        bitset = set()
        for subkey in subkey_indices:
            if len(set(subkey)) != len(subkey):
                raise ValueError(f'Subkey {subkey} has repeated indices.')
            if bitset & set(subkey):
                raise ValueError(f'Subkey {subkey} repeats indices of other subkeys.')
            bitset |= set(subkey)
        if not bitset <= set(range(nbits)):
            raise ValueError(f'Not all bit indices are part of a subkey.')
        if not set(range(nbits)) <= bitset:
            raise ValueError(f'Some subkey indices are not in the key: {set(range(nbits))-bitset}.')
        assert len(subkey_indices) == len(scores)
        for subkey, score_array in zip(subkey_indices, scores):
            assert len(score_array) == 2**len(subkey)
        self.subkey_indices = subkey_indices
        self.scores = [np.asarray(score_vals) for score_vals in scores]
        self.nbits = nbits

    def max_subkey_size(self):
        return max(len(subkey) for subkey in self.subkey_indices)

    def key2subkeys(self, key):
        """Takes the key encoded as a list of bits and returns subkey values
        encoded as lists of bits.
        """
        assert len(key) == self.nbits
        assert all(b in (0, 1) for b in key)
        return [[key[i] for i in subkey] for subkey in self.subkey_indices]

    def key_rank(self, key, acc_bit=1.0, max_nb_bin=2**24):
        """Takes the key encoded as a list of bits and returns and return
        bounds and estimate for the rank of the key.
        """
        subkey_vals = [sum(v*2**i for i, v in enumerate(subkey)) for subkey in self.key2subkeys(key)]
        return scalib.postprocessing.rank_accuracy(
                self.scores,
                np.array(subkey_vals),
                acc_bit=acc_bit,
                max_nb_bin=max_nb_bin,
                )

    def key_rank_ub(self, key, acc_bit=1.0, max_nb_bin=2**24):
        """Takes the key encoded as a list of bits and returns an
        upper-bound for the rank of the key.
        """
        return self.key_rank(key, acc_bit, max_nb_bin)[2]

    def serialize(self):
        """Serialize into a simple datastructure."""
        return {
            'subkey_indices': self.subkey_indices,
            'scores': self.scores,
            'nbits': self.nbits,
            }

    @classmethod
    def deserialize(cls, dump):
        return cls(**dump)
