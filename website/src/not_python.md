# Beyond Python

The challenge framework has been developed to facilitate the development of
python-based submissions. It is however possible to develop submissions using
other languages. 

We suggest two main solutions for this.

- Python C extensions. If want to use native code that can interface with C,
  you can probably turn it into a python module using CPython's C API.
- Subprocess calls. It might be easier to make your actual implementation as a
  standalone script or binary that can be called as a subprocess from
  `quick_eval.py`.

Otherwise, you can use any other technique that works! What matters is that the final apptainer-based test of [Submission](./submission.md) succeeds.

Be sure to include all required installation steps in `setup/setup.sh`.

For native code, you can either:
- Build it in `setup/setup.sh`: this is the most portable option, but requires
  to install the full compilation toolchain in the container.
- Include the binary in the submission package. This might be easier, but be
  careful about native dependencies (or instruction sets -- the evaluation
  server has a AVX2-generation x86 CPU).
  We use this solution for the simulation library in the demo submission, as
  installing verilator would make the container setup very annoying.

