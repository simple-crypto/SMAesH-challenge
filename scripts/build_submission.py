
import argparse
import os
from pathlib import Path
import sys
import zipfile

import itertools as it

def parse_args():
    parser = argparse.ArgumentParser(description='Build a submission package.')
    parser.add_argument(
            '--submission-dir',
            type=Path,
            required=True,
            help='Directory containing the files to be submitted.'
            )
    parser.add_argument(
            '--package-file',
            type=Path,
            required=True,
            help='Path of the .zip file to create.'
            )
    parser.add_argument(
            '--compression',
            choices=['store', 'deflate'],
            default='deflate',
            help=
            'Chose compression algo: deflate (default) or store (no compression).'
            + ' Use store for faster tests.'
            )
    return parser.parse_args()

COMPRESSION_MAP = {
        'store': zipfile.ZIP_STORED,
        'deflate': zipfile.ZIP_DEFLATED,
        }

def create_zip(
    archive_path,
    root_dir,
    zip_prefix,
    compression,
    compresslevel,
    ):
    archive_dir = archive_path.parent
    archive_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=compression,
        compresslevel=compresslevel,
        ) as zf:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            zip_dirpath = os.path.join(zip_prefix, os.path.relpath(dirpath, root_dir))
            for name in it.chain(sorted(dirnames), sorted(filenames)):
                zf.write(
                    os.path.join(dirpath, name),
                    os.path.join(zip_dirpath, name),
                    )

def main():
    args = parse_args()
    if not (args.submission_dir / 'submission.toml').exists():
        print("ERROR: The submission directory does not contain a 'submission.toml' file.", file=sys.stderr)
        return
    create_zip(
        args.package_file,
        args.submission_dir,
        'submission',
        COMPRESSION_MAP[args.compression],
        6,
        )

if __name__ ==  "__main__":
    main()
