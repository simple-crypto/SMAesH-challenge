# FAQ

## How do I choose the claim of my attack?

You can test your attack on the `fk0` dataset. If you did not train on it, then
the number of traces needed to attack `fk0` is *a priori* not different that
the one needed to attack `fk1`.

That being said, for a given attack algorithm, some keys might be easier to
break than some others, and maybe `fk1` is easier or harder than `fk0` for your
attack.
Please do not overfit your attack: develop it while evaluating only on `fk0`,
and when it works there, test it on `fk1`.
You may make multiple attempts at `fk1` while chaning the number of attack
traces, but your final number of traces should work for both `fk0` and `fk1`.


## I have another question.

[Contact us](./introduction.md#contact-information)

