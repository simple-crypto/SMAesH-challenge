
import argparse
import json
from pathlib import Path
import secrets

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
    #src.rename(dest)

manifest_path = Path(args.dataset)

with open(manifest_path, 'rb') as f:
    manifest = json.load(f)

for chunk in manifest['chunks'].values():
    for file in chunk['files'].values():
        file_path = Path(file['path'])
        token = secrets.token_hex()
        new_file_path = file_path.parent / token + file_path.suffix
        files['path'] = new_file_path
        rename(
            manifest_path / file_path,
            manifest_path / new_file_path,
            )

#with open(manifest_path, 'wb') as f:
#    json.dump(manifest)
