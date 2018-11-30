# Logging Experimental Outputs

The `[LOG]` section in every experiment configuration file sets the column names and desired variables for logging.
There is three different output files which can be enabled or disabled as desired:
(1) trial-by-trial outputs for individual sessions;
(2) a summary file recording summaries of experiment blocks;
(3) a summary file recording summaries of the whole session.

By default, _subject_ and _session_ ids are logged to every output file, _block_ id to (1) and (2), and _trial_ id in (1).

There is two configuration fields per output, one defining the column names and variables (`cols_*`), the other one the file name (`*_file_name`).
An output is disabled if the output columns or the output file are commented (i.e. preceded by a `#`);
only when both are present are they enabled.
Note that the file name of the trial-by-trial log differs per participant as each participant's data is logged separately.

## Defining Log Fields

### Variables
Every experiment has its own set of available variables which are listed in the respective config file, and are further described in the respective documentation for the experiment.

### Aggregation

In the block and experiment output, the values can be aggregated or pre-computed by using aggregation functions.
They combine all previously logged data into one output value.
For example to get the average length of a sequence you could use `mean(sequence_length)`, or to get the number of correct trials, or the average length of incorrect trials `mean(sequence_length[correct!=True])`.
The following functions are provided:

- `len` : number of recorded answers, e.g. correct ones
- `max`, `min` : maximum or minimum value
- `mean`, `avg`, `sum` : mean/average, sum of a list of numbers
- `sd`, `var` : standard deviation and variance of a list of numbers

Further, for individual values, the functions `abs` for the absolute value, and `len` for the length of a string, such as the user_input, can be used.

**Note** that as of now, functions cannot be nested or combined, so none of the following examples would work: `mean(len(sequence))`, `mean(similarity) - sd(similarity)`

### Filters

Sometimes in aggregation, one only wants to count specific items, which is why there are some filters provided, that can be applied in square brackets.
Currently, three modes of filtering are implemented:

- `abc(xyz[field])` : to filter for non-False/non-empty items in field
- `abc(xyz[correct==True])` or `abc(xyz[sequence_length==5])` :
to filter for correct items (True) or those of length 5
- `abc(xyz[correct!=True])` or `abc(xyz[sequence_length!=5])` : to filter for incorrect items (not True) or those
   other than length five

<!-- TODO: introduce >, >=, <, <= -->
