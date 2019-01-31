# Release Notes

## 0.2.0 (2019-01-31)

* Makefile: got minutes wanted months
* _base_expyriment
    - Config option for `experiment_text_size` in `[GENERAL]`, which should scale all dependent text sizes downstream; defaults (like expyriment) to 20
    - _show_message now passes `**kwargs` and can stall the screen before continuation is possible

## 0.1.3 (2019-01-24)

Some versions of the android app did not start the main-function automatically. This is fixed now.
All tasks have been tested and shown to work.

## 0.1.2 (2018-12-24)

The ConfigParser class was replaced with a custom class as this was not available on the Android app.
Furthermore some bugs regarding python2/3 compatibility were fixed.

## 0.1.1 (2018-11-30)

Four tasks added:

- Simple Reaction Time Task
- N-Back Task
- Trailmaking Task
- Digit Span Task

Plus a boilerplate for more experiments.
Currently, there are no tutorials or practice sessions implemented.

Add a DOI via [zenodo](https://zenodo.org/).
