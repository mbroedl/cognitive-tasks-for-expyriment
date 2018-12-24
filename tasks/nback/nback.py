#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" N-BACK TASK.
as part of a battery of cognitive tasks for expyriment.

Documentation on this task can be found here:
<https://mbroedl.github.io/cognitive-tasks-for-expyriment/tasks/nback/>

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
from random import choice, randint, random, shuffle
try:
    import android
except ImportError:
    android = None

DEFAULTS = {
    'change_nback_level': 'no',
    'increase_nback_correct_ratio': 0.8,
    'decrease_nback_correct_ratio': 0.5,
    'canvas_size': 0.9,
    'num_boxes': 9,
    'colour_grid': (255, 255, 255),
    'colour_fixation_cross': None,
    'grid_line_width': '1mm',
    'antialiasing': 'yes',
    'reaction_time_only': 'no'
}


class NBack():
    @staticmethod
    def run():
        exp = BaseExpyriment(DEFAULTS)
        nback = NBack(exp)

        nback.start()

        # TODO
        # if SHOW_TUTORIAL:
        #    [showInstructions(exp, n) for n in SHOW_TUTORIAL]

        s = {}
        for id in range(exp.config.getint('DESIGN', 'blocks')):
            block = nback.prepare_block(id, s)
            summary = nback.run_block(block)
            s = summary  # TODO if not block.get_factor('Practice') else s

        exp._log_experiment()

        nback.end()
        return(exp)

    def __init__(self, exp):
        self.exp = exp
        if not android:
            self.exp.mouse.show_cursor()

        # OPTIONAL OPTIONS
        self.line_width = self.exp._unit(self.exp.config.get('APPEARANCE', 'grid_line_width'))
        rel_canvas_size = self.exp.config.getfloat('APPEARANCE', 'canvas_size')
        rel_canvas_size = self.exp.config.getfloat('APPEARANCE', 'canvas_size')
        self.canvas_size = int(
            min(self.exp.screen.window_size[0],
                self.exp.screen.window_size[1] -
                self.exp._unit(self.exp.config.get('APPEARANCE',
                                                   'button_height')) * 2) * rel_canvas_size)
        self.num_boxes = self.exp.config.getint('DESIGN', 'num_boxes')

        self.break_duration = self.exp.config.gettuple('DESIGN', 'break_duration')
        self.display_duration = self.exp.config.getint('DESIGN', 'display_duration')
        self.button_highlight_duration = self.exp.config.getint(
            'DESIGN', 'button_highlight_duration')

        self.trial_options = {
            'P': list(range(self.num_boxes)),
            'C': self.exp._colours(self.exp.config.get('DESIGN', 'colours'))
        }
        # allow for one colour only
        if type(self.trial_options['C'][0]) is int:
            self.trial_options['C'] = [self.trial_options['C']]

        self.grid = self.prepare_grid_stimulus()

    def start(self):
        self.exp._start()

    def end(self):
        self.exp._show_message('', 'thanks')
        self.exp._end()

    def prepare_block(self, id, prev_block={}):
        block = design.Block()
        if id:
            block._id = id
        if self.exp.config.getboolean('DESIGN', 'reaction_time_only'):
            block.set_factor('reaction_time_only', True)
            block.set_factor('nback', 1)
            block.set_factor('nback_mode', 'P')
            if self.exp.config.has_option('DESIGN', 'repeat_probability'):
                block.set_factor('repeat_probability', self.exp.config.getfloat(
                    'DESIGN', 'repeat_probability'))
            else:
                block.set_factor('repeat_probability', 1)
        else:
            block.set_factor('nback', self.exp.config.getforblock('DESIGN', 'nback', id, cast=int))
            block.set_factor('nback_mode', self.exp.config.getforblock('DESIGN', 'nback_mode', id))
            block.set_factor('repeat_probability', self.exp.config.getfloat(
                'DESIGN', 'repeat_probability'))
        block.set_factor('trials', self.exp.config.getforblock('DESIGN', 'trials', id, cast=int))

        self.modes = {'P': 'mode_position',
                      'C': 'mode_colour'}

        if not block.get_factor('reaction_time_only'):
            mode_text = (_('mode_connector') + ' ').join(
                ', '.join([_(self.modes[M]) for M in
                           block.get_factor('nback_mode')]
                          ).rsplit(', ', 1))
            block.set_factor('mode_text', mode_text)

        if prev_block and self.exp.config.getboolean('DESIGN', 'change_nback_level'):
            block.set_factor('nback', max(1,
                                          prev_block['nback'] +
                                          prev_block['correct_ratio'] >= self.exp.config.getfloat('DESIGN', 'increase_nback_correct_ratio') -
                                          prev_block['correct_ratio'] < self.exp.config.getfloat('DESIGN', 'decrease_nback_correct_ratio')))

        for i, trial_item in enumerate(NBack.compute_trial_items(block, self.trial_options)):
            block.add_trial(self.prepare_trial(block, trial_item, i))

        self.exp.add_block(block)
        return(block)

    def prepare_trial(self, block, item, id):
        trial = design.Trial()
        if id:
            trial._id = id
        bx = self.exp.config.getint('DESIGN', 'num_boxes')**(0.5)
        sz = self.canvas_size / bx
        ctr = self.canvas_size / 2

        for k in item:
            if k == 'C':
                trial.set_factor(k, self.exp._invert_colour(item[k]))
            else:
                trial.set_factor(k, item[k])

        s = stimuli.Rectangle([sz, sz], position=[(item['P'] % bx + 0.5) *
                                                  sz - ctr, (item['P'] // bx + 0.5) * sz - ctr], colour=item['C'])
        trial.add_stimulus(s)

        return(trial)

    def run_block(self, block):
        if block.get_factor('reaction_time_only'):
            labels = ['']
        else:
            labels = [_(self.modes[M]) for M in block.get_factor('nback_mode')]
        self.buttons = self.exp.prepare_button_boxes(labels)
        self.canvas = self.new_canvas()
        next_canvas = self.new_canvas()
        self.exp._show_message('', 'block_start', format=block.factor_dict)

        wait = randint(self.break_duration[0], self.break_duration[1])
        self.exp.clock.wait(wait - self.canvas.present() -
                            block.trials[0].stimuli[0].plot(next_canvas) - next_canvas.preload())
        for i, trial in enumerate(block.trials):
            next_canvas, wait = self.run_trial(block, trial, i, next_canvas, wait)

        smry = self.exp._log_block(block)

        def filterNone(l): return [i for i in l if i is not None]
        # create some helpers for the on-screen feedback
        smry_counts = {'len(' + str(k) + ')': sum(filterNone(smry[k])) for k in smry if type(
            smry[k]) is list and type(smry[k][0]) in (int, float)}
        smry_counts.update({'mean(' + str(k) + ')': (sum(filterNone(smry[k])) * 1.0 / len(
            smry[k])) for k in smry if type(smry[k]) is list and type(smry[k][0]) in (int, float)})
        smry_counts.update(smry)
        self.exp._show_message('', 'block_finished', format=smry_counts)
        return(smry)

    def run_trial(self, block, trial, id, next_canvas, wait):
        next_canvas.present()
        self.exp.clock.reset_stopwatch()
        evts = []
        highlight = False
        show = True
        loaded_next_trial = False
        oldwait = wait
        while True:
            if show:
                t = min(self.display_duration - self.exp.clock.stopwatch_time,
                        self.display_duration if not highlight else self.button_highlight_duration)
            else:
                if not loaded_next_trial:
                    next_canvas = self.new_canvas()
                    self.canvas.present()
                    block.trials[id +
                                 1].stimuli[0].plot(next_canvas) if len(block.trials) > id + 1 else []
                    next_canvas.preload()
                    wait = randint(self.break_duration[0], self.break_duration[1])
                    loaded_next_trial = True
                t = min(wait + self.display_duration - self.exp.clock.stopwatch_time, wait +
                        self.display_duration if not highlight else self.button_highlight_duration)
            evt = self.exp.mouse.wait_press(duration=t)
            if not evt[2] and not highlight:
                if show:
                    show = False
                    continue
                else:
                    break
            overlap = [btn for btn in self.buttons if btn.overlapping_with_position(evt[1])]
            if highlight:
                highlight = False
                if show:
                    next_canvas.present()
                else:
                    self.canvas.present()
            if overlap and evt[2]:
                evts.append([overlap[0].label, self.exp.clock.stopwatch_time])
                stimuli.Rectangle(
                    [s - 2*self.line_width for s in overlap[0].size],
                    position=overlap[0].position,
                    line_width=self.line_width * 2,
                    colour=self.exp._colours(
                        self.exp.config.get('APPEARANCE', 'button_highlight_colour'))
                ).present(clear=None)
                highlight = True
        if block.get_factor('reaction_time_only'):
            repeat = True if trial.get_factor('repeat') else False
        else:
            repeat = _(self.modes[trial.get_factor('repeat')]
                       ) if trial.get_factor('repeat') else None
        click, rt = None, None
        idx = False
        if len(evts) > 0:
            pressed, times = zip(*evts)
            idx = repeat in pressed and pressed.index(repeat)
            if idx is False:
                # type check because 0 might be coerced to false
                rt = times[0]
                click = pressed[0]
            else:
                rt = times[idx]
                click = pressed[idx]
        if block.get_factor('reaction_time_only'):
            click = type(click) == str
        results = {
            'wait': oldwait,
            'rt': rt,
            'pressed_any': bool(click) + 0,
            'correct': bool(click == repeat) + 0,
            'correct_repeat': bool(click == repeat and repeat) + 0,
            'incorrect': bool(click != repeat) + 0,
            'missedpositive': bool((not click) and repeat) + 0,
            'falsepositive': bool(click and (not repeat)) + 0,
            'falsebutton': bool(click and repeat and not click == repeat) + 0,
            'corrected': idx is not False and ('|'.join([str(x) for x in times[0:idx]]) if idx > 0 else False),
            'not_last_press': idx is not False and ('|'.join([str(x) for x in times[(idx+1):]]) if len(evts) > idx + 1 else False),
            'repeat': repeat,
            'pressed': click
        }
        self.exp._log_trial(block, trial, results)
        return(next_canvas, wait)

    def new_canvas(self):
        cvs = stimuli.BlankScreen()
        self.grid.plot(cvs)
        [btn.plot(cvs) for btn in self.buttons]
        return(cvs)

    @staticmethod
    def compute_trial_items(block, trial_options):
        num_trials = int(block.get_factor('trials'))
        mode = block.get_factor('nback_mode')
        probability = float(block.get_factor('repeat_probability'))
        nback = int(block.get_factor('nback'))

        log = {}
        for m in mode:
            log[m] = []

        # make repeats
        num_repeat = int(num_trials * probability)
        each_repeat = int(num_repeat / len(mode))
        spare_repeat = num_repeat - each_repeat * len(mode)
        repeats = [''] * (num_trials - num_repeat)
        [repeats.extend([m] * each_repeat) for m in mode]
        [repeats.append(choice(mode)) for i in range(spare_repeat)]
        shuffle(repeats)

        for repeat in repeats:
            next = {}
            for m in trial_options:
                if m not in mode:
                    next[m] = trial_options[m][int(len(trial_options[m])/2)]
            next['repeat'] = repeat
            #findnback = lambda l, n: ([l[-n]] if len(l) >= n else []) if MATCH_EXACTLY else l[-n:]

            def findnback(l, n): return ([l[-n]] if len(l) >= n else [])
            if repeat:
                choose = findnback(log[repeat], nback)
                next[repeat] = choice(choose) if len(choose) > 0 else choice(trial_options[repeat])
                for m in mode:
                    avoid = findnback(log[m], nback)
                    next[m] = choice([x for x in trial_options[m] if x not in avoid]
                                     ) if not m in next else next[m]
                    log[m].append(next[m])
            else:
                for m in mode:
                    # take last nback items
                    avoid = findnback(log[m], nback)
                    # select next item that is not on avoid list
                    next[m] = choice([x for x in trial_options[m] if x not in avoid])
                    log[m].append(next[m])
            yield next

    def prepare_grid_stimulus(self):
        side = self.num_boxes**(0.5)
        block_size = self.canvas_size / side
        center = self.canvas_size / 2
        grid = stimuli.BlankScreen()

        colour_grid = self.exp._colours(self.exp.config.get('APPEARANCE', 'colour_grid'))
        colour_fixation_cross = self.exp._colours(
            self.exp.config.get('APPEARANCE', 'colour_fixation_cross'))
        antialiasing = 10 if self.exp.config.getboolean('APPEARANCE', 'antialiasing') else None

        if colour_grid:
            for a, b in [(i % side, i // side) for i in range(self.num_boxes)]:
                stimuli.Line((a * block_size - center, b * block_size - center), ((a+1) * block_size - center, b *
                                                                                  block_size - center), line_width=self.line_width, colour=colour_grid, anti_aliasing=antialiasing).plot(grid)
                stimuli.Line((a * block_size - center, b * block_size - center), (a * block_size - center, (b + 1) *
                                                                                  block_size - center), line_width=self.line_width, colour=(colour_grid), anti_aliasing=antialiasing).plot(grid)

            stimuli.Line((0 - center, side * block_size - center), (side * block_size - center, side * block_size -
                                                                    center), line_width=self.line_width, colour=colour_grid, anti_aliasing=antialiasing).plot(grid)
            stimuli.Line((side * block_size - center, 0 - center), (side * block_size - center, side * block_size -
                                                                    center), line_width=self.line_width, colour=colour_grid, anti_aliasing=antialiasing).plot(grid)

        if colour_fixation_cross:
            stimuli.FixCross(colour=colour_fixation_cross).plot(grid)
        grid.preload()
        return(grid)


def main():
    NBack.run()


if __name__ == '__main__':
    main()


def showInstructions(exp, nback):
    size = (WIDTH, HEIGHT) if not ROTATE_SCREEN else (HEIGHT, WIDTH)
    tut = stimuli.TextScreen(INSTRUCTIONS['caption_tutorial'][LANGUAGE].format(nback=nback), INSTRUCTIONS['tutorial_text'][LANGUAGE].format(
        nback=nback), size=size, position=(size[0]/3 if ROTATE_SCREEN else 0, -size[1]/3 if not ROTATE_SCREEN else 0))
    tut.rotate(90) if ROTATE_SCREEN else tut
    tut.present()
    exp.mouse.wait_press()

    s = int(SIZE*0.1)
    canvas = stimuli.Rectangle((SIZE, SIZE), colour=misc.constants.C_BLACK)
    littlegrid = nback.prepare_grid_stimulus(line_width=15)
    bx = exp.config.getint('DESIGN', 'num_boxes')**(0.5)
    sz = int(canvas_size / bx)
    ctr = int(canvas_size / 2)

    def drawConnector(text, nback, width):
        vtx = stimuli.Shape(line_width=2)
        halfwidth = int(width / 2 * nback)
        height = int(-width / 3)
        vtx.add_vertices([
            (-halfwidth*1.4, height),
            (-halfwidth *
             0.6, -height),
            (halfwidth*0.6, height)])
        vtx.move((-width / 2 * nback, 0))
        txt = stimuli.TextBox(text, size=(width, width), position=(0, height))
        return(vtx, txt)

    ll = [[5, 0, 5, 6, 6, 5], ['magenta', 'green', 'green', 'cyan', 'green', 'cyan']]
    for l in ll:
        pos = not isinstance(l[0], basestring)
        for i, p in enumerate(l):
            if pos:
                g = littlegrid.copy()
                g.decompress()
                stimuli.Rectangle(
                    (sz, sz),
                    position=((p % bx + 0.5) * sz -
                              ctr, (p // bx + 0.5) * sz - ctr)).plot(g)

                g.scale(0.1)
                g.move((int((i - 2.5) * canvas_size / 6), s*2))
                g.plot(canvas)
            else:
                c = stimuli.Rectangle((int(s/3), int(s/3)), colour=COLOURS[p])
                c.move((int((i - 2.5) * canvas_size / 6), -2*s))
                c.plot(canvas)
            if i >= nback and l[i-nback] == p:
                vtx, txt = drawConnector(INSTRUCTIONS['tutorial_match'][LANGUAGE].format(
                    nback=nback), nback, canvas_size / 6)
                movey = int(1.0 * s)
                if not pos:
                    movey -= int(4*s)
                vtx.move((int((i - 2.5) * canvas_size / 6), movey))
                txt.move((int((i - 2.5) * canvas_size / 6), movey - int(0.5 * s)))
                vtx.plot(canvas)
                txt.plot(canvas)
        if pos:
            txt = stimuli.TextBox(INSTRUCTIONS['tutorial_illustration_colour'][LANGUAGE].format(
                nback=nback), size=(canvas_size, 4*s), position=(0, 2*s))
        else:
            txt = stimuli.TextLine(INSTRUCTIONS['tutorial_illustration_position'][LANGUAGE].format(
                nback=nback), position=(0, int(-1*s)))
        txt.plot(canvas)
    canvas.rotate(90) if ROTATE_SCREEN else canvas
    canvas.present()
    exp.mouse.wait_press()
