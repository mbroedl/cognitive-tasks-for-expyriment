#!/usr/bin/env python
# -*- coding: utf-8 -*-

from expyriment import __version__ as _expyriment_version
from sys import version as _python_version
expyriment_version = [int(i) for i in _expyriment_version.split('.')]
python_version = [int(i) for i in _python_version.split(' ')[0].split('.')]

from expyriment import design, control, stimuli, io, misc
from expyriment import __version__ as _expyriment_version
import os, sys
from ast import literal_eval

if python_version >= [3]:
    from configparser import RawConfigParser, NoOptionError, NoSectionError
else:
    from ConfigParser import RawConfigParser, NoOptionError, NoSectionError

try:
    import android
except ImportError:
    android = None

fallback_dpi = 96

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
        if expyriment_version >= [0,8]:
            _Circle_init(self, radius, anti_aliasing=anti_aliasing, *args, **kwargs)
        else:
            _Circle_init(self, diameter, *args, **kwargs)

stimuli.Circle = _Circle

# PATCHING A BUTTONBOX FAILURE in 0.9
if expyriment_version == [0, 9, 0]:
    _TouchScreenButtonBox_init = io.TouchScreenButtonBox.__init__
    class _TouchScreenButtonBox(io.TouchScreenButtonBox):
        def __init__(self, button_fields, stimuli=[], *args, **kwargs):
            _TouchScreenButtonBox_init(self, button_fields=button_fields, stimuli=stimuli, *args, **kwargs)
            for field in button_fields:
                self.add_button_field(field)
            for stimulus in stimuli:
                self.add_stimulus(stimulus)
    io.TouchScreenButtonBox = _TouchScreenButtonBox

i18n = {}
_ = lambda key: i18n[key] if key else ''

class BaseExpyriment(design.Experiment):
    def __init__(self, default_config = {}):
        self._load_config(default_config)
        design.Experiment.__init__(self, _('title'))
        control.set_develop_mode(self._dev_mode)

        if self.config.has_option('GENERAL', 'window_size') and not self._dev_mode:
            control.defaults.window_size = self.config.gettuple('GENERAL', 'window_size', assert_length=2)
        if self.config.has_option('GENERAL', 'fullscreen') and not self._dev_mode:
            control.defaults.window_mode =  self.config.getboolean('GENERAL', 'fullscreen')
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
            self.data.add_subject_info('session: '+ self._session)

    def _end(self):
        control.end()

    def _load_config(self, defaults = {}):
        defaults = {k: str(v) for k, v in defaults.items()}
        self.config = CustomConfigParser(defaults)
        self.config.read(['config.conf', 'i18n.conf'])

        global i18n
        i18n = dict(self.config.items(self.config.get('GENERAL', 'language')))

        self._dev_mode = False
        if self.config.has_option('DEVELOPMENT', 'active') and self.config.getboolean('DEVELOPMENT', 'active'):
            self._dev_mode = True

    def _show_message(self, caption, text, format={}):
        stimuli.TextScreen(_(caption).format(**format), _(text).format(**format)).present()
        if android:
            self.mouse.wait_press()
        else:
            self.keyboard.wait()

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

    def _log_trial(self, *argv):
        if not self.config.has_option('LOG', 'cols_trial'):
            return

        args = log_args_to_dict(self, *argv)
        col_names = ['subject', 'session', 'block', 'trial'] + [col.strip() for col in self.config.get('LOG', 'cols_trial').split(',')]
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

        col_names = ['subject', 'session', 'block'] + [col.strip() for col in self.config.get('LOG', 'cols_block').split(',')]

        if not self.block_log:
            self.block_log = LogFile(filename=self.config.get('LOG', 'block_summary_file'),
                directory=io.defaults.datafile_directory,
                col_names=col_names)
        self.block_log.add(log_values_to_cols(col_names, args))

    def _log_experiment(self, *argv):
        if not self.config.has_option('LOG', 'cols_experiment') or not self.config.has_option('LOG', 'expriment_summary_file'):
            return
        args = self.trialdata.copy()
        args.update(log_args_to_dict(self, *argv))
        col_names = ['subject', 'session'] + [col.strip() for col in self.config.get('LOG', 'cols_experiment').split(',')]

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

def _clickable_numeric_input(title, start_at):
    # copied from the 0.7.0 release of expyriment
    # https://github.com/expyriment/expyriment/blob/81acb8be1a2abcecdbbfe501e9c4f662c9ba6620/expyriment/control/_experiment_control.py#L96
    background_stimulus = stimuli.BlankScreen(colour=(0, 0, 0))
    fields = [stimuli.Circle(diameter=200, colour=(70, 70, 70),
                             position=(0, 70)),
              stimuli.Circle(diameter=200, colour=(70, 70, 70),
                             position=(0, -70)),
              stimuli.Rectangle(size=(50, 50), colour=(70, 70, 70),
                                position=(120, 0))]
    fields[0].scale((0.25, 0.25))
    fields[1].scale((0.25, 0.25))

        # stimuli.TextLine(text="-", text_size=36, position=(0, -70),
        #                  text_font="FreeMono",
        #                  text_colour=(0, 0, 0)),
    plusminus = [
        stimuli.TextLine(title, text_size=24,
                         text_colour=misc.constants.C_EXPYRIMENT_PURPLE,
                         position=(-182, 0)),
        stimuli.FixCross(size=(15, 15), position=(0, 70),
                         colour=(0, 0, 0), line_width=2),
        stimuli.FixCross(size=(15, 2), position=(0, -70),
                         colour=(0, 0, 0), line_width=2),
        stimuli.TextLine(text = "Go", text_size=18, position=(120, 0),
                         text_colour=(0, 0, 0))]
    number = int(start_at)

    while True:
        text = stimuli.TextLine(
            text="{0}".format(number),
            text_size=28,
            text_colour=misc.constants.C_EXPYRIMENT_ORANGE)
        btn = io.TouchScreenButtonBox(
            button_fields=fields,
            stimuli=plusminus+[text],
            background_stimulus=background_stimulus)
        btn.show()
        key, rt = btn.wait()
        if key == fields[0]:
            number += 1
        elif key == fields[1]:
            number -= 1
            if number <= 0:
                number = 0
        elif key == fields[2]:
            break
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
        done_subjects = [int(x) for x in [y.split('-')[0] for y in existing_files if '-' in y] if x.isdigit()]
        next = max(done_subjects) + 1 if done_subjects else 1

    subject = _numeric_input('SUBJECT ID', next)

    next = 1
    if existing_files:
        done_sessions = [int(z) for z in [y.split('-')[1] for y in existing_files if '-' in y and int(y.split('-')[0]) == int(subject)] if z.isdigit()]
        next = max(done_sessions) + 1 if done_sessions else 1

    session = _numeric_input('SESSION ID', next)

    return(subject, session)


def log_args_to_dict(exp, *argv):
    stash = {'subject': exp._subject, 'session' : exp._session}
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

        if filter and type(value) == list: # FIXME abbreviate?
            if '==' in filter:
                filter_field, filter_value = filter.split('==')
                filter_value = literal_eval(filter_value)
                value = [value[i] for i in range(len(value)) if str(data[filter_field][i]) == str(filter_value)]
            elif '!=' in filter:
                filter_field, filter_value = filter.split('!=')
                filter_value = literal_eval(filter_value)
                value = [value[i] for i in range(len(value)) if str(data[filter_field][i]) != str(filter_value)]
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

mean = lambda ll: sum(ll) * 1.0 / len(ll) if len(ll) >= 1 else None
sd = lambda ll: ( sum((x-mean(ll))**2 for x in ll) / (len(ll)-1) ) ** 0.5 if len(ll) >= 2 else None
var = lambda ll: sum((x - mean(ll)) ** 2 for x in ll) / len(ll)

class LogFile(io.OutputFile):
    # copied and changed from expyriment 0.7.0 source
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
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self._filename = self.standard_file_name
        self._fullpath = directory + "/{0}".format(self._filename)

        atexit.register(self.save)

        add_headers = True if not os.path.exists(self._fullpath) else False
        # Create new file
        fl = open(self._fullpath, 'a+')
        fl.close()
        try:
            locale_enc = locale.getdefaultlocale()[1]
        except:
            locale_enc = "UTF-8"

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
        coerce_list_to_string = lambda l: '|'.join([str(i) for i in l]) if type(l) is list or type(l) is tuple else l
        if type(data) is list or type(data) is tuple:
            if expyriment_version < [0, 9]:
                elements = [io.DataFile._typecheck_and_cast2str(coerce_list_to_string(el)) for el in data]
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
            raise ValueError('Configuration option [{}]:{} needs to be a whole number.'.format(section, option))

    def getfloat(self, section, option, default=None):
        try:
            return self._get(section, float, option, default)
        except ValueError:
            raise ValueError('Configuration option [{}]:{} needs to be a number.'.format(section, option))

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
        if value == 'None':
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
        raise ValueError('Configuration option [{}]:{} needs to have exactly {}{} elements.'.format(section, option, assert_length, ' or 1' if allow_single else ''))
