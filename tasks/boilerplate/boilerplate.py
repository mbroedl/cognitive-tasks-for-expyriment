#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" BOILERPLATE EXPERIMENT.
A boilerplate to create your own experiments, and make use of the
_base_expyriment class as part of a battery of cognitive tasks for expyriment.

Documentation on developing can be found here:
<https://mbroedl.github.io/cognitive-tasks-for-expyriment/howto/developing/>

To run it, you need to have a working copy of python 2.7 or
greater, and expyriment (e.g. via pip) 0.7, 0.9, or greater.

If you use this experiment for any publications, please make
sure to cite the authors as explained in the repository:
<https://mbroedl.github.io/cognitive-tasks-for-expyriment/about/using-and-citing/>

MIT License

Copyright (c) 2018 Malte Rödl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from expyriment import design, control, stimuli, io, misc
from _base_expyriment import BaseExpyriment, _
try:
    import android
except ImportError:
    android = None

DEFAULTS = {
    'value_name': (123, 'abc')
}


class Boilerplate():
    @staticmethod
    def run():
        exp = BaseExpyriment(DEFAULTS)
        boilerplate = Boilerplate(exp)

        boilerplate.start()

        for i in range(exp.config.getint('DESIGN', 'blocks')):
            boilerplate.prepare_block()

        for block in exp.blocks:
            boilerplate.run_block(block)

        exp._log_experiment()

        boilerplate.end()
        return(exp)

    def __init__(self, exp):
        self.exp = exp
        if not android:
            self.exp.mouse.show_cursor()

        # OPTIONAL OPTIONS
        # self.exp.config.gettuple('APPEARANCE', 'value_name')

    def start(self):
        self.exp._start()
        self.exp._show_message('', 'instruction')

    def end(self):
        self.exp._show_message('', 'thanks')
        self.exp._end()

    def prepare_block(self):
        block = design.Block()
        # block.set_factor('block_factor', self.exp.config.getint('DESIGN', 'block_factor'))
        for t in range(self.exp.config.getint('DESIGN', 'trials')):
            block.add_trial(self.prepare_trial(block))
        self.exp.add_block(block)

    def prepare_trial(self, block):
        trial = design.Trial()

        return(trial)

    def run_block(self, block):
        self.exp._show_message('', 'click_to_start')
        for trial in block.trials:
            self.run_trial(block, trial)
        self.exp._log_block(block)

    def run_trial(self, block, trial):
        self.exp._log_trial(block, trial)
        return()


def main():
    Boilerplate.run()


if __name__ == '__main__' or android:
    main()
