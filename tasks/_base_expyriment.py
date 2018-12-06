#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
BASE EXPYRIMENT CLASS
providing additional functions and compatibility to expyriment
versions 0.7 and 0.9, used by all tasks in this battery of cognitive tasks for expyriment.

Documentation on how to develop your own experiments can be found here:
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
'''

import sys
import os
from ast import literal_eval
from expyriment import design, control, stimuli, io, misc

from expyriment import __version__ as _expyriment_version
from sys import version as _python_version
expyriment_version = [int(i) for i in _expyriment_version.split('.')]
python_version = [int(i) for i in _python_version.split(' ')[0].split('.')]


if python_version >= [3]:
    from configparser import RawConfigParser, NoOptionError, NoSectionError
else:
    from ConfigParser import RawConfigParser, NoOptionError, NoSectionError

try:
    import android
except ImportError:
    android = None

fallback_dpi = 96

COLOURS = {
    'black': (0, 0, 0),
    'blue': (0, 0, 255),
    'darkgrey': (150, 150, 150),
    'expyriment_orange': (255, 150, 50),
    'expyriment_purple': (160, 70, 250),
    'green': (0, 255, 0),
    'grey': (200, 200, 200),
    'red': (255, 0, 0),
    'white': (255, 255, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255)
}

DEFAULTS = {
    'button_height': '20mm',
    'button_background_colour': (0, 0, 0),
    'button_border_colour': (80, 80, 80),
    'button_text_colour': 'white',
    'button_highlight_colour': (255, 200, 200),
    'button_highlight_duration': 50
}

# PATCHING THE CIRCLE DIAMETER/RADIUS INCOMPATIBILITY

_Circle_init = stimuli.Circle.__init__


class _Circle(stimuli.Circle):
    def __init__(self, diameter=None, radius=None, anti_aliasing=None, *args, **kwargs):
        if radius and not diameter:
            diameter = 2 * radius
        if diameter and not radius:
            radius = diameter / 2
        if anti_aliasing is True:
            anti_aliasing = 10
        if expyriment_version >= [0, 8]:
            _Circle_init(self, radius, anti_aliasing=anti_aliasing, *args, **kwargs)
        else:
            _Circle_init(self, diameter, *args, **kwargs)


stimuli.Circle = _Circle

# PATCHING A BUTTONBOX FAILURE in 0.9
if expyriment_version == [0, 9, 0]:
    _TouchScreenButtonBox_init = io.TouchScreenButtonBox.__init__
    _TouchScreenButtonBox_create = io.TouchScreenButtonBox.create

    class _TouchScreenButtonBox(io.TouchScreenButtonBox):
        def __init__(self, button_fields, stimuli=[], *args, **kwargs):
            _TouchScreenButtonBox_init(self, button_fields=button_fields,
                                       stimuli=stimuli, *args, **kwargs)
            for field in button_fields:
                self.add_button_field(field)
            for stimulus in stimuli:
                self.add_stimulus(stimulus)

        def create(self):
            _TouchScreenButtonBox_create(self)
            self._canvas.decompress()
            for field in self._button_fields:
                field.plot(self._canvas)
            for stimulus in self._stimuli:
                stimulus.plot(self._canvas)
            self._canvas.preload()
    io.TouchScreenButtonBox = _TouchScreenButtonBox

i18n = {}


def _(key): return i18n[key] if key else ''


class BaseExpyriment(design.Experiment):
    def __init__(self, default_config={}):
        self._load_config(default_config)
        design.Experiment.__init__(self, _('title'))
        control.set_develop_mode(self._dev_mode)

        if self.config.has_option('GENERAL', 'window_size') and not self._dev_mode:
            control.defaults.window_size = self.config.gettuple(
                'GENERAL', 'window_size', assert_length=2)
        if self.config.has_option('GENERAL', 'fullscreen') and not self._dev_mode:
            control.defaults.window_mode = self.config.getboolean('GENERAL', 'fullscreen')
        control.initialize(self)
        if self._dev_mode:
            self.mouse.show_cursor()

        self.expyriment_version = expyriment_version
        self.python_version = python_version

        self.trialdata = None
        self.trial_log = None
        self.block_log = None
        self.experiment_log = None
        self.dev_log = None

        self.screen.dpi = self._get_dpi()

    def _start(self):
        self._session = None
        if self.config.getboolean('GENERAL', 'log_session'):
            subject, session = _prompt_participant_information()
            self._subject = subject
            self._session = session
            self._filename_suffix = '{0}.{0}-{1}'.format(subject.strip(), session.strip())

        control.start(subject_id=int(self._subject))

        if self._session is not None:
            self.data.add_subject_info('session: ' + self._session)

    def _end(self):
        control.end()

    def _load_config(self, defaults={}):
        d1 = DEFAULTS.copy()
        d1.update(defaults)
        d1 = {k: str(v) for k, v in d1.items()}
        self.config = CustomConfigParser(d1)
        self.config.read(['config.conf', 'i18n.conf'])

        global i18n
        i18n = dict(self.config.items(self.config.get('GENERAL', 'language')))

        self._dev_mode = False
        if self.config.has_option('DEVELOPMENT', 'active') and self.config.getboolean('DEVELOPMENT', 'active'):
            self._dev_mode = True

    def _show_message(self, caption, text, format={}, response='both'):
        if caption == 'SKIP' or text == 'SKIP':
            return()
        stimuli.TextScreen(_(caption).format(**format), _(text).format(**format)).present()
        self.keyboard.clear()
        self.mouse.clear()
        while True:
            self.clock.wait(10)
            if (android or response == 'mouse' or response == 'both') and \
                self.mouse.get_last_button_down_event() is not None or \
                (response == 'keyboard' or response == 'both') and \
                    len(self.keyboard.read_out_buffered_keys()) > 0:
                break

    def _in2px(self, size, scale=1):
        if type(size) == str:
            size = float(size)
        if type(size) in (float, int):
            return(self.screen.dpi * size / scale)
        elif type(size) in (tuple, list):
            return([self.screen.dpi * s / scale for s in size])

    def _cm2px(self, size):
        return(self._unit2px(size, 'cm'))

    def _mm2px(self, size):
        return(self._unit2px(size, 'mm'))

    def _unit2px(self, size, unit):
        map_units = {'in': 1, 'cm': 2.54, 'mm': 25.4}
        return(self._in2px(size, map_units[unit]))

    def _unit(self, unit):
        if type(unit) in (int, float):
            return(unit)
        try:
            return(float(unit))
        except ValueError:
            if ',' in unit:
                return([self._unit(u) for u in unit.split(',')])
            return(self._unit2px(float(unit[:-2]), unit[-2:]))

    def _get_dpi(self):
        if self.config.has_option('GENERAL', 'dpi'):
            return(self.config.getint('GENERAL', 'dpi'))
        if android:
            return(android.get_dpi())
        if self.config.has_option('GENERAL', 'screen_diagonal'):
            # NOTE: assuming full screen mode!
            screen_diagonal = self.config.get('GENERAL', 'screen_diagonal')
            width, height = self.screen.window_size
            if 'in' == screen_diagonal[-2:] and not ',' in screen_diagonal:
                return(int((width**2 + height**2)**0.5 / float(screen_diagonal[:-2])))
            elif 'cm' == screen_diagonal[-2:] and not ',' in screen_diagonal:
                return(int((width**2 + height**2)**0.5 / (float(screen_diagonal[:-2]) / 2.54)))
        return(self.config.getint('GENERAL', 'fallback_dpi') if self.config.has_option('GENERAL', 'fallback_dpi') else fallback_dpi)

    @staticmethod
    def _colours(colour):
        if colour.strip() == "" or colour.lower() == "none":
            return(None)
        if colour in COLOURS:
            return(COLOURS[colour])
        if ',' in colour:
            elements = colour.replace('(', '').replace(')', '').replace(
                '[', '').replace(']', '').split(',')
            colours = []
            while len(elements) > 0:
                elements[0] = elements[0].strip()
                if elements[0] in COLOURS:
                    colours.append(COLOURS[elements.pop(0)])
                else:
                    try:
                        colours.append([int(c) for c in elements[:3]])
                        elements = elements[3:]
                    except ValueError:
                        raise ValueError(
                            '"{}" does not represent one or more colours.'.format(colour))
            if len(colours) == 1:
                return(colours[0])
            return(colours)
        raise ValueError('"{}" does not represent one or more colours.'.format(colour))

    @staticmethod
    def _invert_colour(colour):
        if python_version[0] == 3:
            return({v: k for k, v in COLOURS.items()}[colour])
        else:
            return({v: k for k, v in COLOURS.iteritems()}[colour])

    def _log_trial(self, *argv):
        if not self.config.has_option('LOG', 'cols_trial'):
            return

        args = log_args_to_dict(self, *argv)
        col_names = ['subject', 'session', 'block', 'trial'] + \
            [col.strip() for col in self.config.get('LOG', 'cols_trial').split(',')]
        columns = log_values_to_cols(col_names, args)

        if not self.trialdata:
            self.trialdata = dict((arg, []) for arg in args)
        [self.trialdata[arg].append(args[arg]) for arg in args]

        if not self.trial_log:
            self.trial_log = self.data
            self.add_data_variable_names(col_names)

        self.data.add(columns)

        self._log_dev(args)

    def _log_block(self, *argv):
        if not self.config.has_option('LOG', 'cols_block') or not self.config.has_option('LOG', 'block_summary_file'):
            return
        args = self.trialdata.copy()

        block_start_index = args['block'].index(args['block'][-1])
        args = {k: v[block_start_index:] for k, v in args.items()}

        args.update(log_args_to_dict(self, *argv))

        col_names = ['subject', 'session', 'block'] + [col.strip()
                                                       for col in self.config.get('LOG', 'cols_block').split(',')]

        if not self.block_log:
            self.block_log = LogFile(filename=self.config.get('LOG', 'block_summary_file'),
                                     directory=io.defaults.datafile_directory,
                                     col_names=col_names)
        self.block_log.add(log_values_to_cols(col_names, args))
        return(args)

    def _log_experiment(self, *argv):
        if not self.config.has_option('LOG', 'cols_experiment') or not self.config.has_option('LOG', 'expriment_summary_file'):
            return
        args = self.trialdata.copy()
        args.update(log_args_to_dict(self, *argv))
        col_names = ['subject', 'session'] + [col.strip()
                                              for col in self.config.get('LOG', 'cols_experiment').split(',')]

        if not self.experiment_log:
            self.experiment_log = LogFile(filename=self.config.get('LOG', 'experiment_summary_file'),
                                          directory=io.defaults.datafile_directory,
                                          col_names=col_names)
        self.experiment_log.add(log_values_to_cols(col_names, args))

    def _log_dev(self, args):
        if self._dev_mode and self.config.has_option('DEVELOPMENT', 'log_all_variables'):
            keys = sorted(args.keys())
            if not self.dev_log:
                self.dev_log = LogFile(filename=self.config.get('DEVELOPMENT', 'log_all_variables'),
                                       directory=io.defaults.datafile_directory,
                                       col_names=keys)
            self.dev_log.add(log_values_to_cols(keys, args))

    def prepare_button_boxes(self, labels):
        buttons = []
        for i, lb in enumerate(labels):
            width, height = self.screen.window_size
            size = (width / len(labels), self._unit(self.config.get('APPEARANCE', 'button_height')))
            pos = (int(size[0] * (i - len(labels) / 2.0 + 0.5)), -(height - size[1]) / 2)
            btn = stimuli.Rectangle(size=size, position=pos, colour=self._colours(
                self.config.get('APPEARANCE', 'button_background_colour')))
            stimuli.Rectangle(size=size, line_width=5, colour=self._colours(
                self.config.get('APPEARANCE', 'button_border_colour'))).plot(btn)
            text = stimuli.TextLine(text=lb, text_colour=self._colours(
                self.config.get('APPEARANCE', 'button_text_colour')))
            text.plot(btn)
            btn.label = lb
            btn.preload()
            buttons.append(btn)
        return(buttons)


def _clickable_numeric_input(title, start_at, scale=1.0):
    positions = [(100*scale, 0),
                 (-100*scale, 0),
                 (300*scale, -200*scale)]
    btn_colour = misc.constants.C_DARKGREY
    btn_size = (int(70*scale), int(70*scale))
    btn_text_colour = (0, 0, 0)
    pos_title = (0, 100*scale)
    title_text_colour = misc.constants.C_GREY
    number_text_colour = misc.constants.C_GREY

    buttons = [stimuli.Rectangle(size=btn_size, colour=btn_colour, position=pos)
               for pos in positions]

    plus_width = 2*scale if expyriment_version[0] == 7 else 3*scale
    minus_width = 3*scale

    labels = [
        stimuli.TextLine(text='OK', text_size=int(30*scale),
                         position=positions[2], text_colour=btn_text_colour),
        stimuli.FixCross(size=(40*scale, 40*scale),
                         position=positions[0], colour=btn_text_colour,
                         line_width=plus_width),
        stimuli.FixCross(size=(40*scale, 3*scale),
                         position=positions[1], colour=btn_text_colour,
                         line_width=minus_width),
        stimuli.TextLine(title, text_size=int(30*scale),
                         text_colour=title_text_colour, position=pos_title)
    ]

    number = int(start_at)

    while True:
        current_num = stimuli.TextLine(text=str(number),
                                       text_size=int(40*scale),
                                       text_colour=number_text_colour)
        button_box = io.TouchScreenButtonBox(buttons, labels+[current_num])
        button_box.show()
        key = button_box.wait()[0]
        if key == buttons[0]:
            number = number + 1
        elif key == buttons[1]:
            number = max(number - 1, 1)
        elif key == buttons[2]:
            return(number)
    return(number)


def _numeric_input(title, default=''):
    if android:
        return(str(_clickable_numeric_input(title, default)))
    else:
        return(io.TextInput(message=title, length=3).get(str(default)))


def _prompt_participant_information():
    next = 1
    existing_files = None
    if os.path.isdir(io.defaults.datafile_directory):
        existing_files = os.listdir(io.defaults.datafile_directory)
        existing_files = [x.split('.')[-2] for x in existing_files if '.xpd' in x]
        done_subjects = [int(x) for x in [y.split('-')[0]
                                          for y in existing_files if '-' in y] if x.isdigit()]
        next = max(done_subjects) + 1 if done_subjects else 1

    subject = _numeric_input('SUBJECT ID', next)

    next = 1
    if existing_files:
        done_sessions = [int(z) for z in [y.split(
            '-')[1] for y in existing_files if '-' in y and int(y.split('-')[0]) == int(subject)] if z.isdigit()]
        next = max(done_sessions) + 1 if done_sessions else 1

    session = _numeric_input('SESSION ID', next)

    return(subject, session)


def log_args_to_dict(exp, *argv):
    stash = {'subject': exp._subject, 'session': exp._session}
    for arg in argv:
        if type(arg) == dict:
            stash.update(arg)
        if type(arg) == design.Block:
            stash.update(arg.factor_dict)
            stash.update({'block': arg.id})
        if type(arg) == design.Trial:
            stash.update(arg.factor_dict)
            stash.update({'trial': arg.id})
    return(stash)


def log_values_to_cols(column_names, data):
    cols = []
    for col in column_names:
        func = None
        filter = None
        if '(' in col and ')' == col[-1]:
            func, col = col[:-1].split('(')
        if '[' in col and ']' == col[-1]:
            col, filter = col[:-1].split('[')
        value = data.get(col, 'NA')

        if filter and type(value) == list:  # FIXME abbreviate?
            if '==' in filter:
                filter_field, filter_value = filter.split('==')
                filter_value = literal_eval(filter_value)
                value = [value[i] for i in range(len(value)) if str(
                    data[filter_field][i]) == str(filter_value)]
            elif '!=' in filter:
                filter_field, filter_value = filter.split('!=')
                filter_value = literal_eval(filter_value)
                value = [value[i] for i in range(len(value)) if str(
                    data[filter_field][i]) != str(filter_value)]
            else:
                value = [value[i] for i in range(len(value)) if data[filter][i]]

        if func:
            if func not in ['max', 'min', 'avg', 'mean', 'sum', 'abs', 'len', 'sd', 'var']:
                raise ValueError('Function {} not supported for data summary.'.format(func))
            if type(value) is not list and func != 'abs' and func != 'len':
                raise TypeError('Could not find a list for summary column {}.'.format(col))

            value = [v for v in value if v]

            if func == 'avg' or func == 'mean':
                value = mean(value)
            elif func == 'sd' or func == 'sdev':
                value = sd(value)
            elif func == 'var' or func == 'variance':
                value = var(value)
            elif func in __builtins__:
                value = __builtins__[func](value)
            elif func in locals():
                value = locals()[func](value)
            else:
                raise ValueError('Could not locate function {}.'.format(func))
        cols.append(value)
    return(cols)


def mean(ll): return sum(ll) * 1.0 / len(ll) if len(ll) >= 1 else None


def sd(ll): return (sum((x-mean(ll))**2 for x in ll) / (len(ll)-1)) ** 0.5 if len(ll) >= 2 else None


def var(ll): return sum((x - mean(ll)) ** 2 for x in ll) / len(ll)


class LogFile(io.OutputFile):
    def __init__(self, filename, col_names, delimiter=None, comment_char=None, suffix='', directory=''):
        import atexit

        io._input_output.Output.__init__(self)

        self._filename_ = filename
        if delimiter is not None:
            self._delimiter = delimiter
        else:
            self._delimiter = io.defaults.datafile_delimiter

        if comment_char is not None:
            self._comment_char = comment_char
        else:
            self._comment_char = io.defaults.outputfile_comment_char

        self._suffix = suffix
        self._directory = directory

        self._buffer = []
        os.mkdir(directory) if not os.path.isdir(directory) else None

        self._fullpath = directory + "/" + str(self.standard_file_name)

        atexit.register(self.save)

        add_headers = True if not os.path.exists(self._fullpath) else False
        # Create new file
        with open(self._fullpath, 'a+') as f:
            pass

        if add_headers:
            self.add(col_names)

    @property
    def delimiter(self):
        return self._delimiter

    @property
    def standard_file_name(self):
        rtn = os.path.split(sys.argv[0])[1].replace(".py", "")
        return rtn + '_' + self._filename_ + self.suffix

    def add(self, data):
        def coerce_list_to_string(l): return '|'.join(
            [str(i) for i in l]) if type(l) is list or type(l) is tuple else l
        if type(data) is list or type(data) is tuple:
            if expyriment_version < [0, 9]:
                elements = [io.DataFile._typecheck_and_cast2str(
                    coerce_list_to_string(el)) for el in data]
            else:
                elements = [str(coerce_list_to_string(el)) for el in data]
            self.write_line(self.delimiter.join(elements))
        else:
            self.write_line(io.DataFile._typecheck_and_cast2str(data))


class CustomConfigParser(RawConfigParser):
    def get(self, section, option, default=None, **kwargs):
        try:
            if python_version >= [3]:
                return RawConfigParser.get(self, section, option, fallback=default, **kwargs)
            else:
                return RawConfigParser.get(self, section, option, **kwargs)
        except (NoOptionError, NoSectionError) as err:
            print(section, option, default)
            if not default is None:
                return str(default)
            else:
                raise err

    def _get(self, section, conv, option, default=None, **kwargs):
        return conv(self.get(section, option, default, **kwargs))

    def getint(self, section, option, default=None):
        try:
            return self._get(section, int, option, default)
        except ValueError:
            raise ValueError(
                'Configuration option [{}]:{} needs to be a whole number.'.format(section, option))

    def getfloat(self, section, option, default=None):
        try:
            return self._get(section, float, option, default)
        except ValueError:
            raise ValueError(
                'Configuration option [{}]:{} needs to be a number.'.format(section, option))

    def getboolean(self, section, option, default=None):
        try:
            return RawConfigParser.getboolean(self, section, option)
        except (NoOptionError, NoSectionError) as err:
            if not default is None:
                return boolean(default)
            else:
                raise err

    def gettuple(self, section, option, default=None, assert_length=None, allow_single=False, cast_float=False):
        value = self.get(section, option, default).strip()
        if value.lower() == 'none' or value == '':
            return(None)
        if value[0] in '[(' and value[-1] in ')]':
            value = value[1:-1]
        t = [v.strip() for v in value.split(',') if v.strip()]
        try:
            t = [float(v) for v in t] if cast_float else [int(v) for v in t]
        except ValueError:
            pass
        if assert_length is None or \
                len(t) == assert_length or \
                allow_single and len(t) == 1:
            return(t)
        raise ValueError('Configuration option [{}]:{} needs to have exactly {}{} elements.'.format(
            section, option, assert_length, ' or 1' if allow_single else ''))

    def getforblock(self, section, option, block_id):
        value = self.gettuple(section, option,
                              assert_length=self.getint('DESIGN', 'blocks'),
                              allow_single=True)
        return(value[0] if len(value) == 1 else value[block_id])
