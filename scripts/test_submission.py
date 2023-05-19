
import argparse
import itertools as it
import json
import os
from pathlib import Path
import shutil
import subprocess as sp
import zipfile
import venv
import copy
import tomli
import sys

import numpy as np

import dataset
import eval_utils


def parse_args():
    parser = argparse.ArgumentParser(description='Test a submission package.')
    parser.add_argument(
            '--package',
            type=str,
            required=True,
            help="Path to submission zip file. If --package-inplace sepcified, path to the directory containing the submission."
            )
    parser.add_argument(
            '--workdir',
            type=str,
            required=True,
            help='Working directory for testing the submission.',
            )
    parser.add_argument(
            '--empty-workdir',
            default=False,
            action="store_true",
            help='Empty the working directory before starting.',
            )
    parser.add_argument(
            '--dataset-dir',
            type=str,
            required=True,
            help='Directory containing the full profiling dataset (should contain the vk0, fk0).',
            )
    parser.add_argument(
            '--attack-dataset-dir',
            type=str,
            help='Directory containing the attack dataset (default: same as profiling).',
            )
    parser.add_argument(
            '--attack-dataset-manifest-dir',
            type=str,
            help='Directory containing the manifests of the attack dataset (default: --attack-dataset-dir).',
            )
    parser.add_argument(
            '--attack-dataset-name',
            type=str,
            default='fk0',
            help='Name of the attack dataset (default: fk0).',
            )
    parser.add_argument(
            '--package-inplace',
            default=False,
            action="store_true",
            help="Perform the check inplace"
            )
    parser.add_argument(
            '--json',
            default=False,
            action="store_true",
            help="Output JSON evaluation results instead of plain text."
            )
    parser.add_argument(
            '--apptainer',
            default=False,
            action="store_true",
            help="Test in an apptainer container instead of a local python virtualenv.",
            )
    parser.add_argument(
            '--target',
            help='Run only for the given target.',
            )
    parser.add_argument(
            '--only',
            nargs='*',
            choices=['unzip', 'setup', 'profile', 'attack', 'eval'],
            help='Perform only some of the actions in the evaluation, by default run all.',
            )
    return parser.parse_args()

DATASETS_PROFILE = ['vk0', 'fk0']

ATTACK_MANIFEST_NAME = 'manifest_split.json'

ATTACK_FIELDS = ['traces', 'umsk_plaintext']

def _clean_dir(path, re_create=False):
    if os.path.exists(path):
        shutil.rmtree(path)
    if re_create:
        path.mkdir(parents=True)

class SubmissionTest:
    def __init__(self, args):
        self.only_list = args.only
        self.workdir = Path(args.workdir).resolve()
        self.dataset_dir = Path(args.dataset_dir).resolve()
        self.profile_dataset_root = self.dataset_dir
        self.attack_datasets = [args.attack_dataset_name]
        if args.attack_dataset_dir is None:
            self.attack_dataset_dir = self.dataset_dir
        else:
            self.attack_dataset_dir = Path(args.attack_dataset_dir).resolve()
        if args.attack_dataset_manifest_dir is None:
            self.attack_dataset_manifest_dir = self.attack_dataset_dir
        else:
            self.attack_dataset_manifest_dir = Path(args.attack_dataset_manifest_dir).resolve()
        self.custom_attack_dataset_root = self.attack_dataset_dir
        if args.empty_workdir:
            _clean_dir(self.workdir)
        self.workdir.mkdir(exist_ok=True, parents=True)
        self.guess_dir = self.workdir / 'guesses'
        self.custom_attack_dataset_dir = self.workdir / 'custom_attack_datasets'
        self.custom_attack_dataset_dir.mkdir(exist_ok=True, parents=True)
        if args.package_inplace:
            self.submission_dir = Path(args.package)
        else:
            self.submission_dir = self.setup_submission(args.package)
        self.parse_submission()

    def run_setup(self):
        # Create venv
        raise NotImplemented("To be overriden by sub-classes.")

    def only(self, action):
        return not self.only_list or action in self.only_list

    def setup_submission(self, submission_file):
        submission_dir = self.workdir / 'submission'
        if self.only('unzip'):
            _clean_dir(submission_dir)
            zipfile.ZipFile(submission_file, 'r').extractall(self.workdir)
        return submission_dir

    def parse_submission(self):
        with open(self.submission_dir / 'submission.toml', 'rb') as f:
            self.description = tomli.load(f)

    def profile_dir(self, target):
        return (self.workdir / 'profile' / target).resolve()

    def profile_dir_run(self, target):
        return self.profile_dir(target)

    def profile_dataset_args(self, target):
        dataset_dirs = [
                self.profile_dataset_root / target / d / 'manifest.json'
                for d in DATASETS_PROFILE
                ]
        return ['--profile-dataset'] + dataset_dirs

    def run_submission(self, cmd, step, ds_name, target):
        raise NotImplemented("To be overriden by sub-classes.")

    def run_profile(self, target):
        if self.only('profile'):
            _clean_dir(self.profile_dir(target), re_create=True)
            self.run_submission([
                *self.profile_dataset_args(target),
                '--attack-case', target,
                '--save-profile', self.profile_dir_run(target),
                'profile'
                ],
                'profile',
                '_',
                target
                )

    def guess_file(self, ds_name, target):
        return self.guess_dir / target / ds_name / 'guess.msgpack'

    def guess_file_rel(self, ds_name, target):
        return self.guess_file(ds_name, target)

    def attack_dataset_path(self, ds_name, target):
        return self.attack_dataset_manifest_dir / target / ds_name / ATTACK_MANIFEST_NAME 

    def attack_dataset_root(self, ds_name, target):
        return self.attack_dataset_dir / target / ds_name

    def custom_attack_dataset_path(self, ds_name, target):
        return self.custom_attack_dataset_dir / target / ds_name / 'manifest_custom.json'

    def attack_prefix(self, ds_name, target):
        return self.attack_dataset_root(ds_name, target)

    def custom_attack_manifest(self, ds_name, target):
        return self.custom_attack_dataset_path(ds_name, target)

    def write_custom_attack_dataset(self, ds_name, target):
        _clean_dir(self.custom_attack_dataset_path(ds_name, target).parent, re_create=True)
        ds_path = self.attack_dataset_path(ds_name, target).resolve()
        ds_root = self.attack_dataset_root(ds_name, target).resolve()
        ds = dataset.DatasetReader.from_manifest(ds_path)
        ds = _make_attack_dataset(ds, self.description['attacks'][target]['n_traces'])
        def map_ds_path_to_prefix(path):
            rel_path = path.relative_to(ds_root)
            return self.attack_prefix(ds_name, target) / rel_path
        ds.save_to(
                self.custom_attack_dataset_path(ds_name, target),
                process_path=map_ds_path_to_prefix,
                )

    def run_attack(self, target, attacks=None):
        if attacks is None:
            attacks = self.attack_datasets
        if self.only('attack'):
            for ds_name in attacks:
                self.write_custom_attack_dataset(ds_name, target)
                _clean_dir(self.guess_file(ds_name, target).parent, re_create=True)
                self.run_submission([
                    *self.profile_dataset_args(target),
                    '--attack-dataset', self.custom_attack_manifest(ds_name, target),
                    '--attack-case', target,
                    '--load-profile', self.profile_dir_run(target),
                    '--save-guess', self.guess_file_rel(ds_name, target),
                    'attack'
                    ],
                    'attack',
                    ds_name,
                    target
                    )

    def run_eval(self, target, attacks=None):
        if attacks is None:
            attacks = self.attack_datasets
        if self.only('eval'):
            ubs = []
            for ds_name in attacks:
                kg = eval_utils.load_kg(self.guess_file(ds_name, target))
                ubs.append(eval_utils.eval_attack(kg, self.attack_dataset_path(ds_name, target)))
            return np.array(ubs)

def _make_attack_dataset(dataset, n_attack_traces):
    chunk_sizes = [(cv['nexec'], cn) for cn, cv in dataset.chunks.items()]
    chunk_sizes.sort(key=lambda x: x[0],reverse=True)
    tot_nexec = 0
    used_chunks = []
    for nexec, chunk_name in chunk_sizes:
        if tot_nexec + nexec <= n_attack_traces:
            tot_nexec += nexec
            used_chunks.append(chunk_name)
    if tot_nexec != n_attack_traces:
        raise ValueError(
            "Could not make dataset with {n_attack_traces} traces. "
            + "Dataset is too small." if n_attack_traces > len(dataset) else
            "Files are not split in small chunks (use split_dataset.py)."
        )
    return dataset.subset(used_chunks, ATTACK_FIELDS)

class PythonSubmissionTest(SubmissionTest):
    def __init__(self, args):
        super().__init__(args)

    def run_python(self, cmd, cwd=None):
        if cwd is None:
            cwd = self.submission_dir
        cmd = list(cmd)
        env = copy.copy(os.environ)
        env['VIRTUAL_ENV'] = str(self.venv.env_dir)
        env['PATH'] = str(self.venv.bin_path) + ':' + env['PATH']
        return sp.run([self.venv_python] + cmd, check=True, cwd=cwd)

    def run_submission(self, cmd, step, ds_name, _target):
        cmd = ['quick_eval.py'] + cmd
        print(cmd, file=sys.stderr)
        return self.run_python(cmd)

    def run_setup(self):
        venv_dir = self.workdir / 've'
        builder = venv.EnvBuilder(with_pip=True,symlinks=True,clear=self.only('setup'))
        self.venv = builder.ensure_directories(venv_dir)
        if self.only('setup'):
            _clean_dir(venv_dir)
            builder.create(venv_dir)
        self.venv_python = self.venv.env_exec_cmd
        if self.only('setup'):
            self.run_python(['-m', 'pip', 'install', '--upgrade', 'pip'])
            self.run_python(
                    ['-m', 'pip', 'install', '-r', 'requirements.txt'],
                    cwd=self.submission_dir / 'setup'
                    )


DEF_TEMPLATE='''
Bootstrap: docker
From: ubuntu:23.04
%files
    {sub_dir}/setup /setup
%post
    /bin/bash /setup/setup.sh
%environment
    export LC_ALL=C
%labels
    Author AES-HPC Challenge Organisers <info@simple-crypto.dev>
%help
    This is the container for a submission to the AES-HPC challenge.
'''

class ApptainerSubmissionTest(SubmissionTest):
    MEMORY_LIMIT = '128G'
    SETUP_DURATION = 15*60 # s
    PROFILE_DURATION = 4*3600 # s
    ATTACK_DURATION = 4*3600 # s

    SYSTEMD_CMD = f'systemd-run --user --scope -p MemoryMax={MEMORY_LIMIT} -p MemorySwapMax=0'
    APP_EXEC_BASE = 'apptainer exec'
    APP_EXEC_CONTAIN = '--nv --no-mount /etc/localtime -C --net --network none --fakeroot --hostname challenge'
    APP_EXEC = ' '.join([APP_EXEC_BASE, APP_EXEC_CONTAIN])

    PROFILE_ROOT = Path('/profile')
    PROFILE_DS_ROOT = Path('/profile_dataset')
    ATTACK_DS_ROOT = Path('/attack_dataset')
    ATTACK_MANIFEST_ROOT = Path('/attack_manifest')
    GUESS_DIR = Path('/guess')
    SUBMISSION_DIR = Path('/submission')

    def __init__(self, args):
        super().__init__(args)
        self.eval_dir = Path(__file__).parent
        self.profile_dataset_root = self.PROFILE_DS_ROOT
        self.home_dir = self.workdir / 'home'
        self.sif_path = self.workdir / 'submission.sif'
        self.def_path = self.workdir / 'submission.def'

    def attack_prefix(self, ds_name, _target):
        return self.ATTACK_DS_ROOT

    def custom_attack_manifest(self, ds_name, target):
        return self.ATTACK_MANIFEST_ROOT / self.custom_attack_dataset_path(ds_name, target).name

    def profile_dir_run(self, _target):
        return self.PROFILE_ROOT

    def guess_file_rel(self, ds_name, target):
        return self.GUESS_DIR / 'guess.msgpack'

    def run_submission(self, cmd, step, ds_name, target):
        cmd_s = ' '.join(f'"{c}"' for c in cmd)
        home = self.home_dir / step / ds_name
        if home.exists():
            shutil.rmtree(home)
        home.mkdir(parents=True)
        duration = self.PROFILE_DURATION if step == 'profile' else self.ATTACK_DURATION
        mode_profile = 'rw' if step == 'profile' else 'ro'
        app_cmd = self.SYSTEMD_CMD.split(" ")
        app_cmd.extend([
            *self.APP_EXEC.split(' '),
            '-B', f'{self.profile_dir(target)}:{self.PROFILE_ROOT}:{mode_profile}',
            '-B', f'{self.dataset_dir}:{self.PROFILE_DS_ROOT}:ro',
            '-B', f'{self.submission_dir}:{self.SUBMISSION_DIR}:ro',
            ])
        if step == 'attack':
            app_cmd.extend([
                '-B', f'{self.attack_dataset_root(ds_name, target)}:{self.ATTACK_DS_ROOT}:ro',
                '-B', f'{self.custom_attack_dataset_path(ds_name, target).parent}:{self.ATTACK_MANIFEST_ROOT}:ro',
                '-B', f'{self.guess_file(ds_name, target).parent}:{self.GUESS_DIR}:rw',
                ])
        app_cmd.extend([
            '-H', f'{home}:/root',
            self.sif_path
            ])
        app_cmd.extend([
            '/bin/bash',
            '-c',
            f'cd {self.SUBMISSION_DIR}; python3 quick_eval.py {cmd_s}'
            ])
        print(' '.join(map(str, app_cmd)), file=sys.stderr)
        return sp.run(
                app_cmd,
                timeout=duration,
                check=True,
                )

    def run_setup(self):
        if self.only("setup"):
            with open(self.def_path, 'w') as f:
                f.write(DEF_TEMPLATE.format(sub_dir=self.submission_dir))
            sp.run(
                    ['apptainer', 'build', self.sif_path, self.def_path],
                    timeout=self.SETUP_DURATION,
                    check=True,
                    )


def main():
    args = parse_args()
    st = ApptainerSubmissionTest(args) if args.apptainer else PythonSubmissionTest(args)
    st.run_setup()
    if args.target is None:
        targets = list(st.description['attacks'].keys())
    else:
        targets = [args.target]
    results = dict()

    for target in targets:
        st.run_profile(target)
        st.run_attack(target)
        ubs = st.run_eval(target)

        if ubs is not None:
            ubs = np.log2(ubs)
            if not args.json:
                print(f'Attack on target {target}:')
                print('log2 ranks', ubs)
                print('number of successes', np.sum(ubs < eval_utils.MAX_SUCCESS_RANK))
            results[target] = list(ubs)
        else:
            results[target] = None
    if args.json:
        print(json.dumps(results))

if __name__ == '__main__':
    main()

