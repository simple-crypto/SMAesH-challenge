# Beyond Python

The challenge framework has been developed to facilitate the development of
python-only submissions. It is however possible to develop submissions using
other languages. To this end, we advise interested applicants to integrate
their attacks using a dedicated binding. As explained in [Framework](./framework.md), the
evaluation of a submission is done by passing commands to the `quick_eval.py`
utility. In order for the submission to still be evaluated within the
evaluation framework, the behaviour of `quick_eval.py` must be unchanged. In
particular, all modifications are accepted as long as the command-line
interface of `quick_eval.py` is respected.  

