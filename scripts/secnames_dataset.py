
import argparse
import copy
import json
from pathlib import Path
import secrets
import shutil

parser = argparse.ArgumentParser(
    description='Randomize the names of the data files in a dataset.'
    )
parser.add_argument(
        '--dataset',
        type=str,
        required=True,
        help='Existing dataset path (to manifest).',
        )
args = parser.parse_args()

def rename(src, dest):
    print('rename', src, dest)
    src.rename(dest)

manifest_path = Path(args.dataset)

with open(manifest_path, 'rb') as f:
    manifest = json.load(f)

shutil.copyfile(manifest_path, manifest_path.with_suffix('.json.bak'))


for chunk in manifest['chunks'].values():
    for file in chunk['files'].values():
        file_path = Path(file['path'])
        token = secrets.token_hex(16)
        new_file_path = file_path.parent / (token + file_path.suffix)
        file['path'] = str(new_file_path)
        rename(
            manifest_path.parent / file_path,
            manifest_path.parent / new_file_path,
            )

with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=4)
