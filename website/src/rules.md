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
3. Attacks can be submitted at any time on the challenge website as a "submission package" file.
4. A submission can contain attacks for multiple targets. Each attack will be processed independently.
5. The whole challenge (attacks, evaluations, point and prizes) is run indepndently for each target.
6. Each attack comes with a *claim*, which is the number of online traces needed for the attack.
7. Attacks are made public (attack name, team name, submission date and claim) as soon as they are
   submitted. Submission packages are also public, after a 10 days embargo.
8. Sample submissions can be sent to the organizers for testing correct execution of scripts on the evaluation machine.

### Attack evaluation

Each submitted attack will be run for the corresponding private test dataset restricted
to the number of online traces claimed by the attack, using the challenge
evaluation framework.
The attack is successful if the upper-bound on the estimated rank is below
\\(2^{68}\\).
The state of an attack (successful or not) is made public as soon as the
evaluation is done.

### Evaluation limits

- The evaluation will be run on a computer with a Threadripper 3990X processor, a Nvidia A6000 GPU and 128GB of available RAM.
- The execution time of an attack (excluding profiling) will be limited to 4h.

## Grading system

**TL;DR:** You gain 1 point every hour your attack remains the best one.

### Attack acceptance 


Attacks will be evaluated at unspecified and irregular intervals (normally
multiple times a week), in the order in which they have been submitted.

If a team submits a new attack less than 3 days after submitting its previous attack,
and that that previous attack has not been evaluated yet, then it will not be evaluated.

When the time comes to evaluate an attack, if its claim is more than 90% of the
best successful attack evaluated so far, then it is not evaluated (i.e., a 10% improvement is required).

Non-generalizable attacks are not accepted and will not be accepted. An attack
is generalizable if, in addition to being successful, it has a high chance of
being successsful against other test datasets acquired in identical conditions.
In particular, an attack that contains hard-coded information on the test dataset key is not generlizable.

### Points

Points are countinuously awarded for the best successful attack, at the rate of 1 point per hour.

The dates taken into consideration are the date/time of submission of the attack (not the time of evaluation).
The accumulation of points stops when the submission server closes at the end of the challenge.

## Prize

For each target:
- a prize of 1000 € is awarded to the team with the most points,
- a prize of 500 € is awarded to the team with the best attack at the end of the challenge.

The awarded teams will be asked to send a short description of their attacks.
Teams cannot win more than one award.

## Final remarks

- Any time interval of 24 hours is a day.
- You are allowed to use any means you consider necessary to solve the
  challenges, except attacking the infrastructure hosting the challenges or
  extracting unauthorized data from the evaluation environment.
- The organisers reserve the right to change in any way the contest rules or to
  reject any submission, including with retroactive effect.
- Submissions may be anonymous, but only winners accepting de-anonymization
  will get a prize. For this reason, only submissions with a valid correspondence email address will be eligible for prizes.  
- Submissions containing non-generalizable attacks are not accepted and will
  not be accepted. An attack is considered "generalizable" if, in addition to
  being successful, there is a high probability that it will also be
  successful against other evaluation datasets acquired under similar
  conditions.
