# Welcome to the CHES2023 SMAesH Challenge

The SMAesH challenge is a side-channel analysis contest on a masked FPGA
implementation of AES.
Using the public profiling dataset and the open-source hardware design, the
goal is to mount a key-recovery attack using as few traces as possible.

Winners will be announced and rewarded at CHES2023.

**Get started [now](./getting_started.md)!**


## Key features

**Open-source target**: open-source AES implementation running on widespread
SCA board: CW305 and Sakura-G with reproducible acquisition setup.

**Public datasets**: 16 million traces with random key and plaintext, 16
million traces with fixed key and random plaintext, covering 2 AES rounds
(~4,500 samples per trace).

Simple **example attack** (that works) as a starting point: you can easily
start by improving it.

**Profiling challenge**: the profiling dataset for the Artix-7 target (CW305)
contains the values of all the shares in the executions, while the one for the
Spartan-6 (Sakura-G) contains only the unmasked values.

**Attack success criterion**: rank of the key below \\(1
\mathrm{BTCH}\cdot\mathrm{s}\\), defined as the **number of blocks hashed by
the Bitcoin mining network in 1 second** (fixed to \\(2^{68}\\) for the
duration of the challenge).

**Efficient implementation** good latency vs area trade-off with 32-bit wide
masked datapath (4 Sboxes in parallel).

**Arbitrary-order masking**: if you completely break the first-order design, there
is more to come!

## Attack ideas

The organizers of the challenge and designers of the implementation did not
perform advanced attacks on the implementations, but we share our ideas on
potential attack strategies:

- Exploit more leakage points: the demo targets the shares of the S-box output,
  but the following states leak more:
    + masked states in the bitsliced S-box,
    + output of MixColumns,
    + key schedule.
- Use better models than pooled Gaussian Templates.
- Perform cross-dataset transfer learning: you know more on the Artix-7 than on
  the Spartan-6.

## Timeline

- **2023-05-xx** Challenge launch with Artix-7 target, submission server opens.
- **2023-05-xx** Launch of the Spartan-6 target.
- **2023-09-10** (at CHES) Award ceremony.

Submissions are graded continuously, and the [leaderboard](./leaderboard.md)
keeps getting updated.
The best attacks are public: you can get inspiration from other participants,
see the [rules](./rules.md) for more details.

## Contact information

- Mailing list: official announcements and challenge discussions.
- Matrix channel for chatting with other participants, build teams, etc.
- Directly contact the organizers for private matters: <info@simple-crypto.org>.

## Organizers

This challenge is organized by the [SIMPLE-Crypto
Association](https://www.simple-crypto.org), non-profit organization created in
order to develop open source cryptographic implementations and to maintain them
over time, currently with a strong focus on embedded implementation with strong
physical security guarantees.

The contributors involved in this project are Gaëtan Cassiers, Charles Momin
and François-Xavier Standaert.

