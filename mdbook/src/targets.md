# Targets

The targets for this challenge are all instantiations of
[SMAesH](https://github.com/simple-crypto/SMAesH) on FPGAs.
The latter is a 32-bits masked implementation of the [AES-128](https://csrc.nist.gov/publications/detail/fips/197/final) encryption algorithm.
For the challenge, we instantiate it at the first order security (\\(d=2\\)).
For more details, see the [SMAesH documentation](https://www.simple-crypto.org/outputs).

We have two FPGA targets: the [Chipwhisperer CW305](https://rtfm.newae.com/Targets/CW305%20Artix%20FPGA/) with an Artix-7 Xilinx
FPGA and the [Sakura-G](https://satoh.cs.uec.ac.jp/SAKURA/hardware.html) with a Spartan-6 FPGA.

The challenge for the Artix-7 target is in a fully white-box profiled setting:
the full implementation is open-source, including the bitstream.
The profiling datasets for this target include the full seed randomness,
therefore the complete state of the FPGA is known for the profiling traces.
Refer to [Artix-7](./artix7.md) for detailled explanations.

For the Spartan-6, the profiling setting is more constrained: only the SMAesH
core is open-source, and the remaining part of the design is kept secret.  The
profiling datasets for this target only contain the value of the key and the
plaintext.  Of course, challenge participants can perform measurement on their
own instance of SMAesH on a Sakura-G, or use the Artix-7 dataset as a starting
point to build an attack. Refer to [Spartan-6](./spartan6.md) for detailled
explanations.
