# Challenge rules

*The rules of the contest should be interpreted together with all the
documentation material of the contest.*

## Contest Goal

- The goal of the challenge is to design attacks that break the targets a
  minimum of traces for the online phase of the attack.
- "Breaking a target" means extracting a key ranking such that the correct key
  is within enumeration power, fixed to \\(2^{68}\\).
- You can play individually or in teams.
- Multiple targets will be introduced over time.

## Submissions

1. The participants will submit implementations of their attacks and the attacks
   will be evaluated by the organizers.
2. The format and execution interfaces for the submissions is explained in the
   documentation available on the challenge website.
3. Submissions can be submitted at any time on the challenge website.
4. For each target, the submission contains a *claim*, which is the number of online traces needed for the attack.
5. Submissions will be made public over the course of the challenge.
6. You are allowed to use any means you consider necessary to solve the
   challenges, except attacking the infrastructure hosting the challenges or
   extracting unauthorized data from the evaluation environment.
7. Submissions may be anonymous, but only winners accepting de-anonymization will get a prize.
8. Sample submissions can be sent to the organizers for testing correct execution of scripts on the evaluation machine.

### Submission evaluation

For each target covered by the submission, the attack will be run for
the corresponding test dataset, using the provided evaluation framework
restricted to the number of online traces claimed in the submission.
The attack is succesfull if the upper-bound on the estimated rank is below
\\(2^{68}\\).

The result of the evaluation is, for each target where the attack is
successful, a break in \\(n\\) traces where \\(n\\) is the claim.

### Evaluation limits

- The evaluation will be run on a computer with a Threadripper 3990X processor, a Nvidia A6000 GPU and 128GB of available RAM.
- The execution time of an attack will be limited to 2h.

## Grading system

**TL;DR:** Submit your best attack ASAP, improve, run to submit when a attack is
announced and take inspiration from other's attacks.

### Attack acceptance 

Submissions can be submitted at any point in time, and will be evaluated at
unspecified and irregular intervals (normally multiple times a week).
If a team makes a series of submissions separated by less than 6 days, only the
last one is guaranteed to be evaluated: the other ones might not be evaluated
(an already-evaluated attack is never discarded).
The submissions are evaluated following the submission order, and are evaluated independently for each target.

For each target, there is at any point in time a **challenger** attack, which is the best public attack.
(Initially, the challenger is the demo attack or dataset size.)

A submission with a break in a given target, is a *breakthrough attack* for that
target if it reduces by at least 10% the number of online attack traces over
the challenger.
An attack will get points if and only if it is a breakthrough attack.

All *breakthrough attacks* are:

- **announced** on the submission website as soon as they are graded (i.e., only team name and claim),
- **made public** 2 weeks after the announcement (i.e., the full submission is publicly available).
  At this point, it becomes the challenger if it is better than the previous challenger.

*Grace period.*
The above rules imply the existence of a *grace period* of two weeks for competing attacks!
That is, after announcement of a breakthrough attack, a team can submit an
attack with a similar (can be better of worse) claim within two weeks, and get
their attack graded against the current challenger and not the concurrent
breakthrough attack.

### Submission points

Points are awarded for two kinds of achievements:

- improving over the state of the art,
- remaining the state of the art.

More precisely, given the current challenger \\(A_c\\), everytime a new breakthrough attack \\(A_{c'}\\) is made public and becomes the challenger:

1. \\(A_{c'}\\) is awarded \\(t \cdot \log_2(n_{c}/n_{c'})\\) points where
    + \\(t\\) is the number of days since \\(A_c\\) was announced,
    + \\(n_{c'}\\) is the claim of \\(A_{c'}\\),
    + \\(n_{c}\\) is the claim of \\(A_c\\).
2. Each breakthrough attack \\(A\\) announced after \\(A_{c'}\\) was announced ("grace period" submissions) is awarded
  \\(t \cdot \log_2(n_{c}/n_a)\\) points with \\(n_a\\) the claim of \\(A\\).
3. The previous challenger is awarded \\(t \cdot \log_2(1/0.9)\\) points.

Initially, before publication of a challenger, \\(n_{c'}\\) is the number of traces in
an evaluation sub-dataset (or claim of the demo attack if there is one) and the
reference date for \\(t\\) is two weeks before the opening of the submissions for that target.

At the end of the challenge (two weeks after the submission server is closed),
points are awarded to the current challenger following rule 3. above.

### Point accumulation

- The points of a team for a target is the total of the points awarded to their
  attacks for that target.
- Authentication of a team or individual is done with a secret token created on
  the first submission. In case of loss, there are no recovery options.

## Prize

For each target:
- a prize of 1000 € is awarded to the best team,
- a prize of 500 € is awarded to the second best team,

The awarded teams will be asked to send a description of their best attack.

## Final remarks

- The organisers reserve the right to change in any way the contest rules or to reject any submission, including with retroactive effect.

