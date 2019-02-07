#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" DIGIT SPAN TASK.
as part of a battery of cognitive tasks for expyriment.

Documentation on this task can be found here:
<https://mbroedl.github.io/cognitive-tasks-for-expyriment/tasks/digitspan/>

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

# keywords for the android app expyriment.initialize()
from expyriment import design, control, stimuli, io, misc
from _base_expyriment import BaseExpyriment, _
from random import random, randint
from collections import Counter
import difflib
try:
    import android
except ImportError:
    android = None

DEFAULTS = {
    'stimulus_offset': (0, 0),
    'input_offset': (0, 0),
    'foreground_colour': (255, 255, 255),
    'stimulus_colour': (255, 255, 255),
    'background_colour': (0, 0, 0),
    'stimulus_text_size_scale': 6,
    'input_text_size_scale': 3,
    'starting_length': 4,
    'sequence_type': 'numeric',
    'reverse': 'no',
    'duration_display': 800,
    'duration_break': 200
}


class DigitSpan():
    @staticmethod
    def run():
        exp = BaseExpyriment(DEFAULTS)
        digitspan = DigitSpan(exp)

        digitspan.start()

        for i in range(exp.config.getint('DESIGN', 'blocks')):
            digitspan.run_block(block_id=i+1)

        exp._log_experiment()

        digitspan.end()
        return(exp)

    def __init__(self, exp):
        self.exp = exp

        # OPTIONAL OPTIONS
        if self.exp.config.has_section('APPEARANCE'):
            pass
        self.stimulus_offset = self.exp.config.gettuple('APPEARANCE', 'stimulus_offset', assert_length=2)
        self.input_offset = self.exp.config.gettuple('ANDROID' if android else 'APPEARANCE', 'input_offset', assert_length=2)
        self.stimulus_text_size = design.defaults.experiment_text_size * \
            self.exp.config.getint('APPEARANCE', 'stimulus_text_size_scale')
        self.input_text_size = design.defaults.experiment_text_size * \
            self.exp.config.getint('APPEARANCE', 'input_text_size_scale')
        self.stimulus_colour = self.exp.config.gettuple(
            'APPEARANCE', 'stimulus_colour', assert_length=3)
        # TODO
        self.foreground_colour = self.exp.config.gettuple(
            'APPEARANCE', 'foreground_colour', assert_length=3)
        self.background_colour = self.exp.config.gettuple(
            'APPEARANCE', 'stimulus_colour', assert_length=3)

    def start(self):
        self.exp._start()

    def run_block(self, block_id=None):
        block = design.Block()
        if block_id:
            block._id = block_id
        block.set_factor('starting_length',
                            self.exp.config.getforblock('DESIGN',
                                'starting_length', block_id-1, cast=int))
        block.set_factor('reverse',
                            int(self.exp.config.getforblock('DESIGN',
                                'reverse', block_id-1, cast=bool)))
        block.set_factor('sequence_type',
                            self.exp.config.getforblock('DESIGN',
                                'sequence_type', block_id-1))
        seq_length = block.get_factor('starting_length')
        instructions_changed = False
        if block_id > 1 and block.get_factor('reverse') != \
            int(self.exp.config.getforblock('DESIGN','reverse', block_id-2,
                cast=bool)):
            instructions_changed = True
        self.exp._show_message('instruction_title_changed' if
             instructions_changed else 'instruction_title',
             'instruction_reverse' if block.get_factor('reverse') else
             'instruction', stall=8000, heading_bold=True,
             heading_colour=(255,0,0) if instructions_changed else None)
        block.set_factor('trials', self.exp.config.getforblock('DESIGN',
                            'trials', block_id-1, cast=int))
        for t in range(block.get_factor('trials')):
            correct = self.run_trial(block, seq_length, trial_id=t+1)
            seq_length += 1 if correct else -1
            seq_length = max(seq_length, 1)
        self.exp.add_block(block)
        self.exp._log_block(block)

    def run_trial(self, block, seq_length, trial_id=None):
        key = DigitSpan.generate_key(seq_length, block.get_factor('sequence_type'))
        trial = self.prepare_trial(key)
        if trial_id:
            trial._id = trial_id
        block.add_trial(trial)

        self.play_trial(trial)
        correct, user_input = self.user_answer(block, trial)

        self.exp._log_trial(block, trial,
                            {'correct': correct, 'user_input': user_input},
                              DigitSpan.evaluate_trial(user_input[::-1] if
                                block.get_factor('reverse') else user_input,
                              trial.get_factor('sequence')))
        return(correct)

    def prepare_trial(self, key):
        trial = design.Trial()
        for key_pos in key:
            trial.add_stimulus(
                stimuli.TextLine(
                    key_pos,
                    position=self.stimulus_offset,
                    text_colour=self.stimulus_colour,
                    text_size=self.stimulus_text_size))
        trial.set_factor('sequence', key)
        trial.set_factor('sequence_length', len(key))
        return(trial)

    def play_trial(self, trial):
        self.exp._show_message('', 'click_to_start')
        duration_display = self.exp.config.getint('DESIGN', 'duration_display')
        duration_break = self.exp.config.getint('DESIGN', 'duration_break')
        blank = stimuli.BlankScreen()
        self.exp.clock.wait(duration_display / 2 - trial.preload_stimuli() - blank.present())
        for i, stimulus in enumerate(trial.stimuli):
            self.exp.clock.wait(duration_display - stimulus.present())
            self.exp.clock.wait(duration_break - blank.present())
        self.exp.clock.wait(duration_display / 2 - stimuli.BlankScreen().present())

    def user_answer(self, block, trial):
        reverse = block.get_factor('reverse')
        correct_answer = trial.get_factor('sequence')
        seq_length = trial.get_factor('sequence_length')
        input_method = self.exp.config.get('ANDROID', 'input_method')
        if android and input_method == 'keyboard':
            android.show_keyboard()
        self.exp.keyboard.clear()
        if not android or input_method == 'keyboard' or input_method == 'none':
            user_input = io.TextInput(_('remember_sequence_reverse') if
                                        reverse else _('remember_sequence'),
                                        length=seq_length,
                                        position=self.input_offset,
                                        user_text_size=self.input_text_size
                                    ).get().strip()
            android.hide_keyboard() if android else None
        else:
            pass
        answer = user_input[::-1] if reverse else user_input
        format = {'sequence': correct_answer,
                  'sequence_length': seq_length,
                  'sequence_reverse': correct_answer[::-1]}
        if answer.strip() == correct_answer:
            self.exp._show_message('', 'correct_trial', format=format)
        else:
            self.exp._show_message('', 'incorrect_trial_reverse' if reverse else 'incorrect_trial', format=format)
        return(answer == correct_answer, user_input)

    def end(self):
        self.exp._show_message('', 'thanks')
        self.exp._end()

    @staticmethod
    def evaluate_trial(answer, sequence):
        evaluation = {}
        seq_match = difflib.SequenceMatcher(None, answer, sequence)
        matches = seq_match.get_matching_blocks()
        evaluation['longest_match'] = max(matches, key=lambda x: x.size)[2]
        evaluation['total_match'] = sum(m.size for m in matches)
        evaluation['initial_match_answer'] = matches[0].size if matches[0].a == 0 else 0
        evaluation['initial_match_sequence'] = matches[0].size if matches[0].b == 0 else 0
        evaluation['similarity'] = seq_match.ratio()
        return(evaluation)

    @staticmethod
    def generate_key(seq_length, type):
        while True:
            key = ''
            while len(key) < seq_length:
                if type == 'numeric':
                    key += '{:.15f}'.format(random()).split('.')[1][-(seq_length-len(key)):]
                elif type == 'ALPHABETIC' or type == 'ALPHABETICAL':
                    key += chr(randint(65, 90))
                elif type == 'alphabetic' or type == 'alphabetical':
                    key += chr(randint(97, 122))
                else:
                    raise ValueError(
                        'Digit Span type needs to be `numeric` or `alphabetic` or `ALPHABETIC`')
            if DigitSpan.check_key_validity(key):
                return(key)

    @staticmethod
    def check_key_validity(key):
        if sorted(Counter(key).values())[-1] > max(1, len(key) / 4) \
                or sum([1 for i in range(1, len(key)) if key[i] == key[i-1]]) > len(key) / 7 \
                or sum([1 for i in range(2, len(key)) if key[i] == key[i-2]]) > len(key) / 8 \
                or sum([1 for i in range(3, len(key)) if key[i] == key[i-3]]) > len(key) / 9:
            return(False)
        if len(key) >= 2:
            diffs = [ord(key[i]) - ord(key[i-1]) for i in range(1, len(key))]
            if Counter(diffs)[0] > max(1, len(key) / 6) \
                    or sorted(Counter(diffs).values())[-1] > max(1, len(key) / 3) \
                    or sum([1 for i in range(1, len(diffs)) if diffs[i] == diffs[i-1]]) > max(1, len(key) / 16):
                return(False)
        return(True)


def main():
    DigitSpan.run()


if __name__ == '__main__' or android:
    main()
