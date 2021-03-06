# Digit-Span Task

A classic digit-span task for expyriment.

## Configuration

The experiment can be configured in the _config.conf_ file distributed alongside the task.
For the configuration of the `[GENERAL]` block see [Configuration](../../howto/configuration/).

### Experiment Design

The experiment design is covered in the `[DESIGN]` section of the configuration file.
The required configuration for experiment design covers the amount of blocks as well as the amount of trials per block.
For example:

```ini
[DESIGN]
blocks = 1
# * number of trials per block, can vary by block
trials = 10
```

Optional arguments are described below with their default values:

```ini
# * the length of the starting sequence as a whole number
starting_length = 4
# * the type of the sequence to be displayed;
# one of numeric, alphabetic, or ALPHABETIC
sequence_type = numeric
# * whether or not to ask the participant to
# repeat the sequence in reversed order (yes/no)*
reverse = no

# the duration of stimulus display in ms
duration_display = 800
# the break between two stimuli in ms
duration_break = 200
```

The number of trials, as well as starting length, sequence type, and reversal of sequence (indicated by `*`) can either be set as one value for the whole experiment, or one value per block.
So in case of two blocks, it is possible to have `sequence_type = numeric` or `starting_length = 5, 15`;
in this case blocks would use numeric stimuli, but they would start with sequences of length 5 and 15 respectively.

### Appearance

The experiment appearance is covered in the `[APPEARANCE]` section of the configuration file; there are no required arguments.
In the following, the default options are listed.

```ini
[APPEARANCE]
# offset of the displayed numbers;
# the first value is x offset, the second value y offset
stimulus_offset = (0, 0)
# offset of the input box
input_offset = (0, 0)
# the colour of the stimulus in RGB values
stimulus_colour = (255, 255, 255)
# scale of the stimulus compared to normal text
stimulus_text_size_scale = 6
# scale of the input filed compared to normal text
input_text_size_scale = 3

[ANDROID]
## android specific configuration ##
# offset of the input field (see above) as it might overlap
# with the on-screen keyboard
input_offset = (0, 200)
```

### Logging the Experiment

What should be logged is described in the `[LOG]` section of the configuration file.
For a general overview on their configuration, see [here](../../howto/logs/).
The available fields that can be logged are as follows:

* settings, resembling the input to the experiment (may vary per block): `reverse`, `starting_length`, `trials`, `sequence_type`
* computed data per trial: `sequence`, `sequence_length`
* the user response: `user_input`
* analyses of the user response[^difflib]:
    - `correct` : can be True, False
    - `total_match` : the amount of matching digits/characters
    - `longest_match` : the longest continuous match
    - `initial_match_answer` : the number of correct digits/characters at the beginning of the answer
    - `initial_match_sequence` : the number of correctly reproduced digits/characters at the beginning of the given sequence
    - `similarity` : a similarity score calculated as _2 * M / T_ with _M = number of matching digits/characters_ and _T = length of the answer + length of the presented sequence_

[^difflib]: Note that all values apart from whether a sequence is correct are computed using the python difflib; please consult [its documentation](https://docs.python.org/2.7/library/difflib.html) for any queries on how these values come into place.

## Example

A screencast of the first few trials of a Digit Span Task with standard configuration.

![Screencast of the first few trials of a Digit Span Task with standard configuration](../../media/screencast-digitspan.gif)
