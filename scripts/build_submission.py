
import argparse
import fnmatch
import os
from pathlib import Path
import re
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
            '--large-size',
            type=str,
            default='100kB',
            help='Size threshold for "data" files.'
            )
    parser.add_argument(
            '--large-files',
            type=str,
            nargs='*',
            default=tuple(),
            help='Patterns (glob) of the data files.'
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

# based on https://stackoverflow.com/a/60708339
units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}
def parse_size(size):
    size = re.sub(r'([KMGT]?B)', r' \1', size.upper())
    number, unit = [string.strip() for string in size.split()]
    return int(float(number)*units[unit])


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
    large_file_patterns,
    large_file_threshold,
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
            rpath = os.path.relpath(dirpath, root_dir)
            for name in it.chain(sorted(dirnames), sorted(filenames)):
                f = os.path.join(dirpath, name)
                cnt_f = os.path.join(rpath, name)
                zip_f = os.path.join(zip_prefix, cnt_f)
                if os.stat(f).st_size <= large_file_threshold or any(fnmatch.fnmatch(cnt_f, p) for p in large_file_patterns):
                    zf.write(f, zip_f)
                else:
                    print('Skipping large file:', f)

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
        args.large_files,
        parse_size(args.large_size),
        )

if __name__ ==  "__main__":
    main()
