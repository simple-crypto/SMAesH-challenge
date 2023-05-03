# Welcome to the CHES2023 SMAesH Challenge

The SMAesH challenge is a side-channel analysis contest on a masked FPGA
implementation of the AES.
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
\text{BTC-H}\cdot\mathrm{s}\\), defined as the **number of blocks hashed by
the Bitcoin mining network in 1 second** (fixed to \\(2^{68}\\) for the
duration of the challenge).

**Efficient implementation** good latency vs area trade-off with 32-bit wide
masked datapath (4 Sboxes in parallel).

**Arbitrary-order masking**: if you completely break the first-order design, there
is more to come!

## Attack ideas

The demo submission implements a textbook attack against the AES S-box output that should be 
easy to improve. We next share a few ideas of alternative strategies that could be used for this purpose: 

- Exploit more leakage points: the demo targets the shares of the S-box output
  which lies in the combinatorial logic, but the masked states in the bitslice
  S-box or the output of MixColumns leak more.
- Profile larger target intermediate values: for example, the masked states in
  the bitslice S-box are larger than 8-bit despite they only depend on 8 key
  bits, and the output of MixColumns naturally depends on 32 key bits.
- Perform multi-target and multivariate attacks: there are multiple leaking
  operations in the implementations, which can be exploited with advanced
  statistical attacks (e.g., analytical strategies or machine learning).
- Try different profiling strategies: for low number of shares, directly
  profiling with a machine learning model without taking advantage of the
  shares' knowledge could be possible.
- Perform cross-dataset transfer learning: we provide more profiling power for
  the Artix-7 than for the Spartan-6.
- Exploit the leakage of the key scheduling algorithm. 

## Timeline

- **May 2023** Challenge launch with Artix-7 target, submission server opens.
- **June 2023** Launch of the Spartan-6 target.
- **2023-09-1** Submission server closes.
- **2023-09-10** (at CHES) Award ceremony.

Submissions are graded continuously, and the [leaderboard](./leaderboard.md)
keeps getting updated.
The best attacks are public: you can get inspiration from other participants,
see the [rules](./rules.md) for more details.

## Contact information

- Mailing list: announcements and challenge discussions.
[[send a mail]](mailto:smaesh-challenge@freelists.org)
[[subscribe]](https://www.freelists.org/list/smaesh-challenge)
[[list archive]](https://www.freelists.org/archive/smaesh-challenge/)
- [Matrix channel](https://matrix.to/#/#smaesh-challenge:matrix.org) for chatting with other participants, build teams, etc.
- Directly contact the organizers for private matters: <info@simple-crypto.org>.

## Organizers

This challenge is organized by the [SIMPLE-Crypto
Association](https://www.simple-crypto.org), a non-profit organization created in
order to develop open source cryptographic implementations and to maintain them
over time, currently with a strong focus on embedded implementation with strong
physical security guarantees.

The contributors involved in this project are Gaëtan Cassiers, Charles Momin
and François-Xavier Standaert.

