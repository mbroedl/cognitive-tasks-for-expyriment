# Release Notes

## 0.2.0 (2019-01-31)

* Makefile
    - build wrongly used minutes instead of months for filenames
    - now throws an error if not on master or if uncommited changes — can be avoided with any value to the `FORCE` parameter (e.g. `make build FORCE=yes`)
* _base_expyriment
    - Config option for `experiment_text_size` in `[GENERAL]`, which should scale all dependent text sizes downstream; defaults (like expyriment) to 20
    - new function `_load_block_settings` appends settings to block (trial possible as well) dynamically and adds factors to block and trial output if varying across blocks
    - implement `median` function for aggregated output
    - translations accessed by underscore (`_`) are utf-8 decoded now (previously non-ascii characters could throw an error if they were logged to the events file)
    - _show_message
        - now passes `**kwargs` to stimuli.TextScreen
        - can stall the screen (`stall=` in ms) before continuation is possible
        - a block can be passed (`block=`) to allow customised captions:
        - all texts can now be adjusted to a practice block using `caption_key[practice]`
        - specific blocks can have different texts using for example `caption_key[block:2]` (1-indexed)
        - captions (the top) can now be highlighted (bold + red) using `caption_key[highlight] = yes`
        - they can all be combined in the order listed here, so
          `caption_key[practice][block:2][highlight]` highlights caption_key in block two if it is a practice block

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
