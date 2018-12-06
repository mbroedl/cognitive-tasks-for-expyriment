#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""TRAIL-MAKING TASK.
as part of a battery of cognitive tasks for expyriment.

Documentation on this task can be found here:
<https://mbroedl.github.io/cognitive-tasks-for-expyriment/tasks/trailmaking/>

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
from _base_expyriment import BaseExpyriment, _, python_version
from random import randint
import itertools
try:
    import android
except ImportError:
    android = None

DEFAULTS = {
    'on_pointer_release': 'reset',
    'on_mismatched_circle': 'repeat_last',
    'target_radius': '5mm',
    'line_width': '1.5mm',
    'stimulus_relative_text_size': 1.5,
    'stimulus_text_correction_y': 0.2,
    'target_font': 'sans',
    'min_distance_of_targets': 4,
    'attempts_before_reducing_min_distance': 200,
    'colour_line': (0, 255, 0),
    'colour_target': (255, 255, 0),
    'colour_target_label': (0, 0, 0),
    'colour_target_done': (0, 255, 0),
    'colour_target_error': (255, 0, 0),
    'colour_target_hint': (0, 255, 0),
    'colour_window_boundary': None,
    'antialiasing': 'yes'
}


class TrailMaking():
    @staticmethod
    def run():
        exp = BaseExpyriment(DEFAULTS)
        trail_making = TrailMaking(exp)

        for i in range(exp.config.getint('DESIGN', 'blocks')):
            trail_making.prepare_block(i)

        trail_making.start()
        for block in exp.blocks:
            trail_making.run_block(block)

        exp._log_experiment()

        trail_making.end()
        return(exp)

    def __init__(self, exp):
        self.exp = exp
        if not android:
            self.exp.mouse.show_cursor()

        # OPTIONAL OPTIONS
        self.radius = self.exp._unit(self.exp.config.get('APPEARANCE', 'target_radius'))
        self.line_width = self.exp._unit(self.exp.config.get('APPEARANCE', 'line_width'))
        self.ring_radius = self.radius - self.line_width / 2

        self.colour_line = self.exp.config.gettuple('APPEARANCE', 'colour_line')

        self.antialiasing = self.exp.config.getboolean('APPEARANCE', 'antialiasing')
        self.colour_target = self.exp.config.gettuple('APPEARANCE', 'colour_target')

        self.colour_target_done = self.exp.config.gettuple('APPEARANCE', 'colour_target_done')
        self.colour_target_error = self.exp.config.gettuple('APPEARANCE', 'colour_target_error')
        self.colour_target_hint = self.exp.config.gettuple('APPEARANCE', 'colour_target_hint')

        self.colour_target_label = self.exp.config.gettuple('APPEARANCE', 'colour_target_label')
        self.target_font = self.exp.config.get('APPEARANCE', 'target_font')
        self.stimulus_text_correction_y = self.exp.config.getfloat(
            'APPEARANCE', 'stimulus_text_correction_y')

        self.stimulus_relative_text_size = self.exp.config.getfloat(
            'APPEARANCE', 'stimulus_relative_text_size')

        self.on_pointer_release = self.exp.config.get('DESIGN', 'on_pointer_release')
        self.on_mismatched_circle = self.exp.config.get('DESIGN', 'on_mismatched_circle')

        self.labels = TrailMaking.make_labels()

    def start(self):
        self.exp._start()
        # self.exp._show_message('', 'instruction')

    def end(self):
        self.exp._show_message('', 'thanks')
        self.exp._end()

    def prepare_block(self, id):
        block = design.Block()
        block.set_factor('num_targets', self.exp.config.getforblock('DESIGN', 'num_targets', id))
        block.set_factor('target_titles', self.exp.config.getforblock(
            'DESIGN', 'target_titles', id))
        block.set_factor('timeout', self.exp.config.getforblock('DESIGN', 'timeout', id))
        for t in range(self.exp.config.getforblock('DESIGN', 'trials', id)):
            block.add_trial(self.prepare_trial(block))
        self.exp.add_block(block)

    def prepare_trial(self, block):
        trial = design.Trial()
        # TODO: practice = e['Practice'] if 'Practice' in e else False
        labels = self.labels[block.get_factor('target_titles')][:block.get_factor('num_targets')]

        positions = TrailMaking.make_random_positions(
            self.exp.screen.window_size,
            self.radius,
            block.get_factor('num_targets'),
            self.exp.config.getfloat('DESIGN', 'min_distance_of_targets') * self.radius,
            self.exp.config.getfloat('DESIGN', 'attempts_before_reducing_min_distance'))

        for lab, pos in zip(labels, positions):
            stim = stimuli.Circle(radius=self.radius, position=pos,
                                  colour=self.colour_target,
                                  anti_aliasing=self.antialiasing)
            label = stimuli.TextBox(lab,
                                    (self.radius*2, self.radius*2),
                                    text_size=int(self.stimulus_relative_text_size * self.radius),
                                    position=[pos[0], pos[1] -
                                              self.stimulus_text_correction_y * self.radius],
                                    text_justification=1,
                                    text_colour=self.colour_target_label,
                                    text_font=self.target_font)
            trial.add_stimulus(stim)
            trial.add_stimulus(label)
        return(trial)

    def run_block(self, block):
        # self.exp._show_message('', 'click_to_start')
        for trial in block.trials:
            self.run_trial(block, trial)
        # self.exp._log_block(block)

    def run_trial(self, block, trial):
        trial = block.trials[0]

        def display_labels(lbls): return ' - '.join(lbls[:6]) + (' - ...' if len(lbls) > 6 else '')
        target_order = display_labels(self.labels[block.get_factor('target_titles')])
        self.exp._show_message('', 'instruction', format={'target_order': target_order})

        idoffset = trial.stimuli[1].id - 1

        def make_surface(trial):
            sf = stimuli.BlankScreen()
            boundary = self.exp.config.gettuple('APPEARANCE', 'colour_window_boundary')
            if boundary:
                stimuli.Rectangle(self.exp.screen.window_size,
                                  line_width=self.line_width,
                                  colour=boundary).plot(sf)
            [s.plot(sf) for s in trial.stimuli]
            return sf

        surface = make_surface(trial)
        surface.present()

        cumulated = 0
        path = []
        currentcircle = 0
        score = 0
        mouse = self.exp.mouse.position
        has_moved = False

        logs = {'lost_touch': [], 'touched_targets': []}

        def get_log(evt): return {
            '_block': block.id + 1,
            'current_target': currentcircle,
            'distance': cumulated,
            'time': self.exp.clock.stopwatch_time,
            'score': score,
            'event': evt
        }

        in_circle = -1
        mismatched_circles = []
        misc.Clock.reset_stopwatch(self.exp.clock)

        while True:
            new_mouse = self.exp.mouse.wait_motion(duration=20)[0]
            if self.exp.clock.stopwatch_time / 1000 >= block.get_factor('timeout'):
                self.exp._log_trial(block, trial, get_log('timeout'))
                break
            if self.exp.mouse.pressed_buttons[0] != 1:
                lost = False
                if currentcircle > 0 or len(mismatched_circles) > 0:
                    lost = True
                if self.on_pointer_release == 'reset':
                    currentcircle = 0
                    mismatched_circles = []
                    score = 0  # TODO
                    has_moved = False
                    surface = make_surface(trial)
                    surface.present()
                elif self.on_pointer_release == 'nothing':
                    pass
                if lost:
                    logs['lost_touch'].append(get_log('lost_touch'))
                    self.exp._log_trial(block, trial, logs['lost_touch'][-1])
                continue
            if mouse == new_mouse:
                continue
            if not has_moved:
                has_moved = True
                mouse = None
                continue
            if abs(new_mouse[0]) >= self.exp.screen.window_size[0]/2 or abs(new_mouse[1]) >= self.exp.screen.window_size[1]/2:
                continue
            if mouse is not None:
                stimuli.Line(mouse, new_mouse, self.line_width, self.colour_line).plot(surface)
                stimuli.Circle(radius=self.line_width/2,
                               position=new_mouse,
                               colour=self.colour_line,
                               anti_aliasing=self.antialiasing
                               ).plot(surface)
                cumulated += TrailMaking.point_distance(new_mouse, mouse)
                path.append([new_mouse[0], new_mouse[1], self.exp.clock.stopwatch_time])

            def get_stimulus_position(sid): return [
                x for x in trial.stimuli if x.id == sid][0].position

            for s in trial.stimuli:
                if 'Circle' in s.__class__.__name__:
                    x, y = s.position
                    if TrailMaking.point_distance((x, y), new_mouse) <= self.radius:
                        if in_circle == -1:
                            in_circle = s.id
                            if (s.id - idoffset)/2+0 == currentcircle:
                                # stimuli.Circle(radius=CIRCLE_SIZE, colour=COLOUR_CIRCLE_DONE, line_width=LINEWIDTH, position=(x, y)).plot(surface)
                                # , anti_aliasing=ANTIALIASING
                                currentcircle += 1
                                # score += SCORE_CORRECT_CIRCLE
                                logs['touched_targets'].append(get_log('correct_touch'))
                                self.exp._log_trial(block, trial, logs['touched_targets'][-1])
                                if len(mismatched_circles) > 0:
                                    for ss in mismatched_circles + [s.id]:
                                        trial.stimuli[ss - idoffset].plot(surface)
                                        trial.stimuli[ss - idoffset + 1].plot(surface)
                                    mismatched_circles = []
                            elif (s.id - idoffset)/2+0 < currentcircle - 1 or (s.id - idoffset)/2+0 > currentcircle:
                                if self.on_mismatched_circle == 'repeat_last':
                                    if len(mismatched_circles) == 0 and currentcircle > 0:
                                        currentcircle -= 1
                                    stimuli.Circle(radius=self.ring_radius, colour=self.colour_target_hint, line_width=self.line_width, position=get_stimulus_position(
                                        currentcircle*2 + idoffset)).plot(surface)
                                if self.on_mismatched_circle in ['highlight_only', 'repeat_last']:
                                    mismatched_circles.append(s.id)
                                    stimuli.Circle(radius=self.ring_radius,
                                                   colour=self.colour_target_error,
                                                   line_width=self.line_width,
                                                   position=(x, y),
                                                   anti_aliasing=self.antialiasing).plot(surface)
                                # score += SCORE_WRONG_CIRCLE
                                logs['touched_targets'].append(
                                    get_log('wrong_touch:' + str(currentcircle)))
                                self.exp._log_trial(block, trial, logs['touched_targets'][-1])
                    else:
                        if in_circle == s.id and TrailMaking.point_distance((x, y), new_mouse) >= self.radius + 1:
                            trial.stimuli[in_circle - idoffset + 1].plot(surface)
                            in_circle = -1
            surface.present()
            mouse = new_mouse
            if currentcircle >= len(trial.stimuli)/2:
                self.exp._log_trial(block, trial, get_log('finish'))
                break
        logs['time'] = self.exp.clock.stopwatch_time
        logs['distance'] = cumulated
        logs['score'] = score
        self.exp._show_message('', 'trial_done', format={
                               'distance': logs['distance'], 'time': logs['time'], 'score': logs['score']})

        self.exp._log_block(trial, block, logs, {'trail': trial.id},
                            TrailMaking.make_trail_summary(logs, block))
        # TODO
        # self.log_trail(block, path)
        # self.log_targets(block, block.trials[0].stimuli)
        return()

    @staticmethod
    def make_labels():
        labels = {
            '123': list(map(str, range(1, 99))),
            'abc': list(map(chr, range(97, 123))),
            'ABC': list(map(chr, range(65, 91)))
        }

        zip_longest = itertools.izip_longest if python_version[0] == 2 else itertools.zip_longest

        def alternate_lists(a, b): return [
            x for x in itertools.chain.from_iterable(zip_longest(a, b)) if x]

        def alternate_lists_skip(a, b):
            a, b = list(a), list(b)
            length = min(len(a), len(b))
            lst = a[:length]
            lst[1::2] = b[1:length:2]
            return(lst)

        labels['1a2'] = alternate_lists(labels['123'], labels['abc'])
        labels['a1b'] = alternate_lists(labels['abc'], labels['123'])
        labels['1A2'] = alternate_lists(labels['123'], labels['ABC'])
        labels['A1B'] = alternate_lists(labels['ABC'], labels['123'])
        labels['1b2'] = alternate_lists_skip(labels['123'], labels['abc'])
        labels['a2c'] = alternate_lists_skip(labels['abc'], labels['123'])

        return(labels)

    @staticmethod
    def make_random_positions(area, radius, num_positions, min_distance, min_attempts):
        positions = []
        for i in range(num_positions):
            failed_position = 0
            while True:
                p = randint(int(-area[0]/2 + radius), int(area[0]/2 - radius)
                            ), randint(int(-area[1]/2 + radius), int(area[1]/2 - radius))
                if not [1 for x in positions if TrailMaking.point_distance(p, x) < min_distance]:
                    positions.append(p)
                    break
                else:
                    failed_position += 1
                    if failed_position > min_attempts:
                        return(TrailMaking.make_random_positions(area, radius, num_positions, min_distance - 0.05 * radius, min_attempts))
        return(positions)

    @staticmethod
    def point_distance(a, b):
        return(((a[0] - b[0])**2 + (a[1] - b[1])**2)**(0.5))

    @staticmethod
    def make_trail_summary(results, block):
        # calculate minimum distance for connecting the paths
        mindist = 0
        for tid in range(2, len(block.trials[0].stimuli), 2):
            mindist += TrailMaking.point_distance(
                block.trials[0].stimuli[tid].position, block.trials[0].stimuli[tid-2].position)

        return(
            {
                'num_lost_touch': len(results['lost_touch']),
                'num_wrong_targets': len([1 for x in results['touched_targets'] if x['event'].startswith('wrong')]),
                'num_done_targets': max([x['current_target'] for x in results['touched_targets'] if x['event'].startswith('correct')]),
                'min_distance': mindist,
                'ratio_min_distance': results['distance'] / mindist
            }
        )


def main():
    TrailMaking.run()


if __name__ == '__main__':
    main()


def logTrail(exp, block, path):
    if not SUMMARY_LOG_PRACTICE and block.get_factor('Practice'):
        return
    if TRAIL_LOG_FILE_NAME:
        p = exp.subject
        b = block.id + 1
        fname = exp.data.directory + '/' + \
            TRAIL_LOG_FILE_NAME.format(subject_id=p, session_id=exp.session, block_id=b)
        if not os.path.isfile(fname):
            with open(fname, "w") as f:
                f.write(','.join(['participant', 'block', 'x', 'y', 'time']) + '\n')
        with open(fname, 'a') as f:
            [f.write(','.join([str(x) for x in [p, b] + pth]) + '\n') for pth in path]


def logTargets(exp, block, stimuli):
    if not SUMMARY_LOG_PRACTICE and block.get_factor('Practice'):
        return
    if TARGETS_LOG_FILE_NAME:
        p = exp.subject
        b = block.id + 1
        fname = exp.data.directory + '/' + \
            TARGETS_LOG_FILE_NAME.format(subject_id=p, session_id=exp.session, block_id=b)
        if not os.path.isfile(fname):
            with open(fname, "w") as f:
                f.write(','.join(['participant', 'block', 'label', 'x', 'y']) + '\n')
        with open(fname, 'a') as f:
            for s in stimuli:
                if s.__class__.__name__ == 'Circle':
                    x, y = s.position
                if s.__class__.__name__ == 'TextBox':
                    lab = s.text
                    f.write(','.join([str(x) for x in [p, b, lab, x, y]]) + '\n')
