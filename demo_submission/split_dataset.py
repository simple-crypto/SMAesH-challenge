
import argparse
import math
from pathlib import Path

import dataset

parser = argparse.ArgumentParser(
    description='Split the last file of a dataset to have power-of-two nexec in files.'
    )
parser.add_argument(
        '--dataset',
        type=str,
        required=True,
        help='Existing dataset path (to manifest).',
        )
parser.add_argument(
        '--new',
        type=str,
        default="manifest_split.json",
        help='Name of the new manifest.',
        )
args = parser.parse_args()

dest_path = Path(args.dataset).parent / args.new

dr = dataset.DatasetReader.from_manifest(args.dataset)
chunks = list(dr.chunks.items())

with dataset.DatasetWriter(dest_path, dr.id+'splitbin', dr.metadata, dr.fields) as dw:
    for chunk_name, chunk in chunks[:-1]:
        dw.add_existing_chunk(chunk_name, chunk)
    last_chunk_name,  last_chunk = chunks[-1]
    loaded_chunk = dr.load_chunk(last_chunk_name)
    for base in reversed(range(int(math.log2(last_chunk['nexec'])))):
        dw.add_chunk(
                last_chunk_name + f'_split{base}',
                **{f: c[2**base:2**(base+1),...] for f, c in loaded_chunk.items()}
                )
    dw.add_chunk(
            last_chunk_name + f'_split00',
            **{f: c[0:1,...] for f, c in loaded_chunk.items()}
            )

