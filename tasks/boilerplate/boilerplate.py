from expyriment import design, control, stimuli, io, misc
from _base_expyriment import BaseExpyriment, _
try:
    import android
except ImportError:
    android = None

DEFAULTS = {
    'value_name' : (123, 'abc')
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

if __name__ == '__main__':
    main()
