
"""Dataset documentation

A dataset contains a collections of power consumption traces and execution
setting for a series of executions of a target along with metadata. The dataset
is stored over multiple files and directories.

# Data model

The dataset contains a set of `nexec` executions, which is split in multiple
chunks (not necessarily all of the same size).
For each execution, there is a leakage traces of `nsamples` samples, where each
sample is a signed 16-bit integer, and also some input data which is a byte
array of length `nindata`. The content of the input data is described at [TODO,
wrapper of the implementation].
Moreover, the dataset as some associated metadata, which is a JSON object.

## Metadata

Here is the metadata that is found in our datasets:
{
    "info": "Human-readable description.",
    "bsfile_hash": "Hash of the bitstream for the target. Format: sha256-<hex of hash>.",
    "sample_rate": <oscilloscope sample rate>,
    "vrange": <oscilloscope vertical range>,
    "mes_chain": "<description of the measurement chain (oscilloscope, probe)>",
    "target_serial": "<serial number of the target>",
    TODO: what should we add ?
}

# Stored representation

The main component of a dataset is its manifest file (the 'dataset path' is the
path to the manifest file). The manifest file contains a json object of the
form:
{
    "about": "SIMPLE-DATASET-MANIFSET",
    "version": "1.0",
    "id": "org.simple-crypto:CTF-AESHPC2-1/<dataset_part>",
    "metadata": <metadata object>,
    "fields": {
        "<field_name>": {
            shape: [<shape of the data>, ...],
            dtype: "<data type>",
        }
    }
    "chunks": { <chunk name>: <chunk object>, ...}
}
where a chunk object is
{
    "nexec": <number of executions in chunk>,
    "files": { "<field_name>": <file object>, ...  }
}
and a file object is
{
    "path": <path relative to the directory containing the manifest>,
    "hash": "Hash of the content of the file. Format: sha256-<hex of hash>."
}

The files containing the traces and the indata are .npy files [1].

A design principle is that all information about the dataset (except the data
itself) must be contained in the manifest, such that any processing pipeline
may be configured (including buffer allocation) before reading the data.

[1] https://numpy.org/devdocs/reference/generated/numpy.lib.format.html


# Partial datasets

A dataset may be partial, that is, some of the files listed in the manifest may
not exist.
"""

import bisect
import hashlib
import itertools as it
import json
import pathlib
import copy

import numpy as np

class DatasetError(Exception):
    pass

class PartialDatasetError(DatasetError):
    pass

class CorruptedDatasetError(DatasetError):
    pass

class DatasetReader:
    def __init__(self, dataset_id, metadata, chunks, fields, base_path):
        self.id = dataset_id
        self.metadata = metadata
        self.chunks = chunks
        self.fields = fields
        self.base_path = base_path
        self.cum_nexec = list(it.accumulate([0] + [chunk['nexec'] for chunk in self.chunks.values()]))
        self.chunk_name_list = list(self.chunks)
        self.chunk_list = list(self.chunks.values())

    def __len__(self):
        return self.cum_nexec[-1]

    @classmethod
    def from_manifest(cls, manifest_path, base_path=None,perm_seed=None):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        if manifest.get('about') != 'SIMPLE-DATASET-MANIFEST':
            raise DatasetError('Manifest file does not have SIMPLE-DATASET-MANIFEST marker.')
        if base_path is None:
            base_path = pathlib.Path(manifest_path).resolve().parent
        else:
            base_path = pathlib.Path(base_path).resolve()
        try:
            if manifest['version'] != '1.0':
                raise DatasetError(f'Unknown manifest version {manifest["version"]}.')
            dataset_id = manifest['id']
            metadata = manifest['metadata']
            if perm_seed==None:
                chunks = manifest['chunks']
            else:
                # Apply a permutation
                rs = np.random.RandomState(seed=perm_seed)
                manifest_keys = list(manifest['chunks'].keys())
                random_keys = rs.permutation(manifest_keys)
                chunks = {k:manifest['chunks'][k] for k in random_keys}
            fields = {
                    f_name: { "shape": f["shape"], "dtype": np.dtype(f["dtype"]) }
                    for f_name, f in manifest['fields'].items()
                    }
        except KeyError as e:
            raise DatasetError("Badly-formed manifest.") from e
        else:
            return cls(dataset_id, metadata, chunks, fields, base_path)

    def _chunk_paths(self, chunk_name):
        chunk = self.chunks[chunk_name]
        return {f: self.base_path / p['path'] for f, p in chunk['files'].items()}

    def chunk_exists(self, chunk_name):
        return all(path.exists() for path in self._chunk_paths(chunk_name).values())

    def is_partial(self):
        return any(not self.chunk_exists(chunk_name) for chunk_name in self.chunks)

    def validate_chunk(self, chunk_name, allow_missing=False):
        if allow_missing and not self.chunk_exists(chunk_name):
            return
        for f, path in self._chunk_paths(chunk_name).items():
            hash_scheme = 'sha256-'
            h = self.chunks[chunk_name]['files'][f]['hash'].partition(hash_scheme)
            if h[:2] != ('', hash_scheme):
                raise DatasetError('Hash not SHA256.')
            try:
                if _sha256sum(path) != h[2]:
                    raise CorruptedDatasetError('Hash mismatch.')
            except OSError as e:
                raise PartialDatasetError(f'chunk {chunk_name}') from e

    def validate(self, allow_missing=True):
        for chunk_name in self.chunks:
            self.validate_chunk(chunk_name, allow_missing)

    def load_chunk(self, chunk_name, mmap_mode=None, fields=None):
        """Load a dataset chunk.
        Returns {'traces': <trace array>, 'indata': <indata array>}.

        mmap_mode: see [1], default: None, you may get better performance using 'r'.
        [1] https://numpy.org/doc/stable/reference/generated/numpy.memmap.html
        """
        return {
                f: np.load(path, mmap_mode=mmap_mode)
                for f, path in self._chunk_paths(chunk_name).items()
                if fields is None or f in fields
                }

    def iter_ntraces(self, max_ntraces=None, start_trace=0, fields=None, max_chunk_size=None):
        # Let max_ntraces be in range
        if max_ntraces is None:
            max_ntraces = self.cum_nexec[-1] - start_trace
        else:
            max_ntraces = min(max_ntraces, self.cum_nexec[-1] - start_trace)
        if max_ntraces == 0:
            # Handle special empty case
            chunk_names = []
            chunk_slices = []
        else:
            # Indices of chunks to be loaded.
            start_chunk = bisect.bisect_right(self.cum_nexec, start_trace) - 1
            end_chunk = bisect.bisect_left(self.cum_nexec, start_trace+max_ntraces)
            # Names of the loaded chunks and range of trace offsets in them
            chunk_names = self.chunk_name_list[start_chunk:end_chunk]
            start_range_start = start_trace - self.cum_nexec[start_chunk]
            end_range_end = start_trace + max_ntraces - self.cum_nexec[end_chunk-1]
            chunk_ranges = [
                    (start_range_start, self.chunks[chunk_names[0]]["nexec"]),
                    *[(0, self.chunks[cn]["nexec"]) for cn in chunk_names[1:-1]],
                    (0, end_range_end),
                    ]
            # Fixup in case of a single chunk
            if start_chunk == end_chunk-1:
                chunk_ranges = [(chunk_ranges[0][0], chunk_ranges[1][1])]
            # Slices in chunks
            chunk_slices = [
                    _split_slice(start, stop, max_chunk_size)
                    for start, stop in chunk_ranges
                    ]
        return ChunkIterator(self, chunk_names, chunk_slices, fields)

    def subset(self, chunk_names=None, fields=None):
        if chunk_names is not None:
            chunk_names = set(chunk_names)
        new_fields = {
                fn: fv for fn, fv in self.fields.items()
                if fields is None or fn in fields
                }
        new_chunks = {
                cn: {
                    'nexec': cv['nexec'],
                    'files': {
                        fn: fv for fn, fv in cv['files'].items() if fields is None or fn in fields
                        },
                    }
                for cn, cv in self.chunks.items()
                if chunk_names is None or cn in chunk_names
                }
        return type(self)(self.id, self.metadata, new_chunks, new_fields, self.base_path)

    def subset_ntraces(self, n_traces, fields=None):
        chunk_sizes = [(cv['nexec'], cn) for cn, cv in self.chunks.items()]
        chunk_sizes.sort(key=lambda x: x[0],reverse=True)
        tot_nexec = 0
        used_chunks = []
        for nexec, chunk_name in chunk_sizes:
            if (n_traces == None) or (tot_nexec + nexec <= n_traces):
                tot_nexec += nexec
                used_chunks.append(chunk_name)
        if tot_nexec != n_traces and n_traces != None:
            raise ValueError(
                f"Could not make dataset with {n_traces} traces. "
                + "Dataset is too small." if n_traces > len(self) else
                "Files are not split in small chunks (use split_dataset.py)."
            )
        return self.subset(used_chunks, fields)

    def save_to(self, manifest_path, process_path=None):
        manifest_path = pathlib.Path(manifest_path).resolve()
        new_basepath = manifest_path.parent
        new_chunks = copy.deepcopy(self.chunks)
        def map_path(path):
            try:
                return path.relative_to(new_basepath)
            except ValueError:
                return path
        if process_path is None:
            process_path = map_path
        for chunk in new_chunks.values():
            for f in chunk['files'].values():
                f['path'] = str(process_path((self.base_path / f['path']).resolve()))
        new_ds = type(self)(self.id, self.metadata, new_chunks, self.fields, new_basepath)
        with open(manifest_path, 'w') as f:
            f.write(new_ds.serialize())
        
    def serialize(self):
        return _gen_manifest(self.id, self.metadata, self.chunks, self.fields)


class DatasetWriter:
    """
    dataset_path: str
    fields: {<field_name>: { 'shape': [<shape of one record>], 'dtype': np.dtype }, ...}
    """
    def __init__(self, dataset_path, dataset_id, metadata, fields):
        self.path = pathlib.Path(dataset_path)
        self.id = dataset_id
        self.metadata = metadata
        self.fields = fields
        # convert e.g. np.int8 to np.dtype('int8')
        for f in self.fields.values():
            f['dtype'] = np.dtype(f['dtype'])
        self.chunks = dict()
        self.error = False

    def add_existing_chunk(self, chunk_name, chunk):
        self.chunks[chunk_name] = chunk

    def add_chunk(self, chunk_name=None, **fields):
        if chunk_name is None:
            chunk_name = '{:04}'.format(len(self.chunks))
        if not isinstance(chunk_name, str) or chunk_name in self.chunks:
            self.error = True
            raise ValueError('Bad chunk_name.')
        nexec = next(iter(fields.values())).shape[0]
        if set(fields) != set(self.fields):
            self.error = True
            raise ValueError('Bad field set.')
        for field_name, f_type in self.fields.items():
            field_data = fields[field_name]
            exp_shape = tuple([nexec] + f_type['shape'])
            if field_data.shape !=  exp_shape:
                self.error = True
                raise ValueError(
                        f'Bad field shape {field_name}.' +
                        f' Expected {exp_shape}, got {field_data.shape}.'
                        )
            if field_data.dtype != f_type['dtype']:
                self.error = True
                raise ValueError(
                        f'Bad field type {field_name}.' +
                        f' Expected {f_type["dtype"]}, got {field_data.dtype}.'
                        )
        chunk = dict(nexec=nexec, files=dict())
        for field_name in self.fields:
            p = self.path.parent / field_name / (chunk_name + '.npy')
            p.parent.mkdir(parents=True, exist_ok=True)
            np.save(p, fields[field_name])
            h = _sha256sum(p)
            chunk['files'][field_name] = dict(
                    path = str(pathlib.Path('.') / field_name / (chunk_name + '.npy')),
                    hash = 'sha256-' + h,
                    )
        self.chunks[chunk_name] = chunk

    def write_manifest(self):
        manifest = _gen_manifest(self.id, self.metadata, self.chunks, self.fields)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w') as f:
            f.write(manifest)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None and not self.error:
            self.write_manifest()

def _split_slice(start, stop, max_chunk_size):
    if max_chunk_size is None:
        return [(start, stop)]
    else:
        starts = list(it.takewhile(lambda x: x<stop, it.count(start, max_chunk_size)))
        ends = starts[1:] + [stop]
        return [(start, stop) for start, stop in zip(starts, ends)]

class ChunkIterator:
    def __init__(self, dataset_reader, chunk_names, chunk_slices, fields=None):
        self._dataset_reader = dataset_reader
        self._chunk_names = chunk_names
        self._chunk_slices = chunk_slices
        self.fields = fields
        self._i = 0

    def __iter__(self):
        def inner():
            for cn, cs in zip(self._chunk_names, self._chunk_slices):
                chunk = self._dataset_reader.load_chunk(cn, fields=self.fields, mmap_mode='r')
                for start, stop in cs:
                    yield {f: array[start:stop,...] for f, array in chunk.items()}
        return inner()

    def __len__(self):
        return sum(len(cs) for cs in self._chunk_slices)

    @property
    def n_traces(self):
        return sum(cs.stop-cs.start for slices in self._chunk_slices for cs in slices)


def _gen_manifest(dataset_id, metadata, chunks, fields, pretty=True):
    manifest = dict(
            about="SIMPLE-DATASET-MANIFEST",
            version="1.0",
            id=dataset_id,
            metadata=metadata,
            fields={
                f_name: {'shape': f['shape'], 'dtype': f['dtype'].str}
                for f_name, f in fields.items()
                },
            chunks=chunks,
            )
    return json.dumps(manifest, indent=4 if pretty else None)

def _sha256sum(path):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(path, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

