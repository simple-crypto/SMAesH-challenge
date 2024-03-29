# Welcome to the SMAesH Challenge

The SMAesH challenge is a side-channel analysis contest on
[SMAesH](https://simple-crypto.org/activities/smaesh),
a masked FPGA
implementation of the AES.
Using the public profiling dataset and the open-source hardware design, the
goal is to mount a key-recovery attack using as few traces as possible.

The SMAesH challenge was the [CHES2023 challenge](https://ches.iacr.org/2023/challenge.php).

**Get started [now](./getting_started.md)!**

**The winners were announced at the CHES2023 rump session
[slides](https://raw.githubusercontent.com/simple-crypto/SMAesH-challenge-submissions/main/CHES2023_slides.pdf),
but the challenge continues: see the [leaderboard](./leaderboard.md) and new
[submission instructions](./submission.md)!**

N.B.: We maintain a list of all attacks, including those that are not proper
submissions (e.g., do not follow the correct format or do not respect the
rules): please [send them to us](mailto:info@simple-crypto.org).

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

- Try to re-use the demo submission with fewer traces! This is a quick and
  efficient way to gain points for early candidates. 
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

You can also have a look at the [existing open-source attacks](./leaderboard.md)!

## Timeline

- **2023-05-08** Challenge launch with Artix-7 target, submission server opens.
- **2023-07-03** Launch of the Spartan-6 target.
- **2023-09-1** Submission server closes.
- **2023-09-10** (at CHES) Award ceremony.
- **2023-10-19!** Full dataset public release. The challenge [continues with self-evaluation](./submission.md)! See the [leaderboard](./leaderboard.md).

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

