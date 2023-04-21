
import argparse

import attack
from dataset import DatasetReader
import msgpack
import os

import msgpack_numpy

import numpy as np
import key_guess
import eval_utils

msgpack_numpy.patch(allow_pickle=False)

# TODO --start-trace

def parse_args():
    parser = argparse.ArgumentParser(description='Quick attack evaluation.')
    parser.add_argument(
            '--profile-dataset',
            type=str,
            nargs='*',
            help='Path to the manifest of the profiling datasets.',
            )
    parser.add_argument(
            '--attack-case',
            type=str,
            required=True,
            help='Name of the attack case.',
            )
    parser.add_argument(
            '--attack-dataset',
            type=str,
            help='Path to the manifest of the attack dataset.',
            )
    parser.add_argument(
            '--n-attack-traces',
            type=int,
            help='Number of traces for the attack.',
            )
    parser.add_argument(
            '--save-profile',
            type=str,
            help='Directory where the profiling data should be saved.',
            )
    parser.add_argument(
            '--load-profile',
            type=str,
            help='Directory where the profiling data should be loaded.',
            )
    parser.add_argument(
            '--save-guess',
            type=str,
            help='File where the attack results (scores) are stored.',
            )
    parser.add_argument(
            '--load-guess',
            type=str,
            help='File where the attack results (scores) are loaded from.',
            )
    parser.add_argument(
            "--offset-atck-traces",
            type=int,
            default=0,
            help="Offset in the attack dataset"
            )
    parser.add_argument(
            'actions',
            choices=['profile', 'attack', 'eval'],
            nargs='+',
            )
    parser.add_argument(
            '--chunk-seed',
            type=int,
            default=None,
            help="Seed for the chunk permtation applied when reading the dataset"
            )
    parser.add_argument(
            '--max-chunk-size',
            type=int,
            default=None,
            help="Maximum size of the chunk returned by the dataset reader."
            )
    return parser.parse_args()

def kg_encoder(obj):
    if isinstance(obj, key_guess.KeyGuess):
        return {'type': '__keygyess', 'val': obj.serialize()}
    elif isinstance(obj, np.ndarray):
        bio = io.BytesIO()
        np.lib.format.write_array(bio, obj)
        return {'type': '__npndarray', 'val': bio.getvalue()}
    else:
        return obj

def kg_objhook(obj):
    if obj.get('type') == '__keygyes':
        return key_guess.KeyGuess.deserialize(obj['val'])
    elif obj.get('type') == '__npndarray':
        bio = io.BytesIO(obj['val'])
        return np.lib.format.read_array(bio)
    else:
        return obj

def main():
    args = parse_args()
    at = attack.Attack(args.attack_case)
    if 'profile' in args.actions:
        # make this a vec based on dataset names TODO nope, rather use
        # test_submission for that
        at.profile([DatasetReader.from_manifest(p,perm_seed=args.chunk_seed) for p in args.profile_dataset])
        if args.save_profile:
            os.makedirs(args.save_profile, exist_ok=True)
            at.save_profile(args.save_profile)
    if 'attack' in args.actions:
        if args.load_profile and 'profile' not in args.actions:
            at.load_profile(args.load_profile)
        attack_dataset = DatasetReader.from_manifest(args.attack_dataset,perm_seed=args.chunk_seed)
        # TODO check with final dataset format. Make constant re-used by test_submission.
        kg = at.attack(
                attack_dataset.subset_ntraces(args.n_attack_traces, fields=['traces', 'umsk_plaintext'])
                )
        if args.save_guess:
            with open(args.save_guess, 'wb') as f:
                msgpack.dump(kg.serialize(), f)
    if 'eval' in args.actions:
        if 'attack' not in args.actions:
            kg = load_kg(args.load_guess)
        ub = eval_attack(kg, args.attack_dataset)
        print('log2 rank', np.log2(ub))
        print('success', ub < eval_utils.MAX_SUCCESS_RANK)

if __name__ == "__main__":
    main()
