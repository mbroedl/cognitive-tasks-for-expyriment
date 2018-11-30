# Trail-Making Task

A trail-making task for expyriment.


## Configuration

The experiment can be configured in the _config.conf_ file distributed alongside the task.
For the configuration of the `[GENERAL]` block see [Configuration](../../howto/configuration/).
Particularly on android devices it might be advisable to change the `window_size` as this task is very computing intensive and might lag otherwise, as described in the link.

### Experiment Design

The experiment design is covered in the `[DESIGN]` section of the configuration file.
The required configuration for experiment design covers the amount of blocks as well as the amount of trials per block.
For example:

```ini
[DESIGN]
blocks = 3
## all of the following values can be one of these values to
## repeat for all blocks, or as many values as there
## are blocks and separated by commas; in case of two blocks:
## e.g. target_titles = 123 OR target_titles = 123, abc
## three values for two blocks or vice versa causes an error
## amount of trials (i.e. trails to make per block)
trials = 1
## default amount of targets per trial
num_targets = 10, 20, 30
## the labels of targets, the values below are possible, and
## continued as is to be expected; note that '1a2' is alternating
## numbers and the alphabet, whereas '1b2' is skipping labels
## maximum number of targets are 26 for 'abc', '1b2', and 'a2c',
## 52 for '1a2', 'a1b', etc, and 99 for '123'
## one of: 123, abc, 1a2, a1b, A1B, 1A2, 1b2, a2c
target_titles = 123, 1a2, 1a2
## timeout for the task in seconds; when this time was reached
## this the task will be ended automatically
timeout = 100, 200, 300
```

Optional parameters and their default values:

```ini
## how to handle when the screen is not touched anymore
## reset : remove all lines drawn and start with the first
## circle again, while time is continued [default]
## nothing : nothing happens
on_pointer_release = reset

## how to handle a wrong circle
## repeat_last : participants needs to touch the last completed
## circle again, score decreases [default]
## highlight_only : wrong circle is highlighted, score
## decreases, target stays as before
on_mismatched_circle = repeat_last
```

### Appearance

The experiment appearance is covered in the `[APPEARANCE]` section of the configuration file; there are no required arguments.
In the following, the default options are listed.

```ini
## units for the following two options can be mm, cm, in,
## or no unit for pixels
## the radius of circles
target_radius = 5mm
## line width for drawing
line_width = 1.5mm

## size of text on a target relative to its radius
stimulus_relative_text_size = 1.5
## baseline correction of the text in the circles relative
## to radius. this depends on text size and font, and corrects
## for the non-existent part of text below the line
stimulus_text_correction_y = 0.2
## font of the text in the circle, None for Standard font,
## otherwise a font name without spaces, e.g. 'timesnewroman',
## 'arial', 'courier', or 'console'. this will affect the
## size of the text even though font size remains constant
target_font = sans

## minimum distance between circles in multiple of radius;
## 2 means the closest they can get is touching each other
## too high values mean that circles will be almost presented
## in a grid-like way with high target numbers, whereas low
## values can mean clustering the exact values when this occurs
## depend on the screen size
min_distance_of_targets = 4
## if the minimum distance is too high and circles are too big
## the program will stall. this setting aborts the positioning
## after the amount of attempts specified to place a circle in
## the existing surroundings. it then reduces the minimum
## distance requirement by .05 of the target radius
attempts_before_reducing_min_distance = 200

#### COLOURS
## Colours are presented in RGB format
## colour of the drawn line
colour_line = 0, 255, 0
## colour of targets
colour_target = 255, 255, 0
## colour of text on tagets
colour_target_label = 0, 0, 0
## colour of any circle touched in the right order
colour_target_done = 0, 255, 0
## colour of any circle touched wrongly
colour_target_error = 255, 0, 0
## colour of the circle to go back to
colour_target_hint = 0, 255, 0
## colour of the window boundary, None for no boundary
## this is helpful if the resolution you choose does not match
## the screen resolution on an android device
colour_window_boundary = None

## anti aliasing is about whether to smoothen edges; unused
## in the android app and other setups running expyriment 0.7.0
## as it does not support antialiasing for circles
antialiasing = yes
```

### Logging the Experiment

What should be logged is described in the `[LOG]` section of the configuration file.
For a general overview on their configuration, see [here](../../howto/logs/).
Note that in the log, every _event_ in the trail making task is logged, which is one of

* _correct_touch_ if a target was correctly connected to the trail
* _wrong_touch_ if a wrong target was connected to the trail; note that this is logged as _wrong_touch:15_ if the circle 15 (not the circle with label 15!) was connected
* _lost_touch_ if the user released the finger from the screen (touchpad) or stopped holding the mouse button pressed (desktop)
* _timeout_ if the user faced a timeout
* _finish_ if the last target was connected to the trail

The available fields that can be logged are as follows:

* settings, resembling the input to the experiment: `timeout`, `num_targets`, `target_titles`
<!-- computed data per trial: target positions -->
<!-- the user response: path -->
* tracking of the user response:
    - `event` : any of the events as described above
    - `distance` : distance travelled so far
    - `time` : time taken so far
    - `current_target` : the target number that needed to be connected when that event happened

The block summary for the trail making task is logged after making a trail was finished;
in case you set `trials` to anything higher than 1, multiple trails will be summarised here.
The following convenience fields are available to this summary:

- `time` : time in ms taken to complete the task; in case of a timeout it should be equal or bigger than the timeout
- `distance`: the distance travelled in pixel; this includes deleted paths and those that were reset through lost touch
- `num_lost_touch` : amount of times the user lost touch with the screen
- `num_wrong_targets` : the number of times a wrong target was connected to the trail
- `num_done_targets` : the highest target number that could be connected; should be identical to `num_targets` unless a timeout occurred
- `min_distance` : the minimum distance necessary to connect all items if connected by straight lines
- ratio_min_distance : the distance travelled divided by the minimum distance
- `lost_touch` : list of events when the user lost touch (see above; note that printing this will print a list of python dictionaries to the output)
- `touched_targets` : list of events when a target was touched (note that printing this will print a list of python dictionaries to the output)

These further items can be aggregated in the experiment summary if required.

## Example

A screencast of a trail-making task with standard settings, 20 targets and the order _1-A-2-B-3-C-..._

    ![Screencast of the first few trials of a Trail-Making Task with standard configuration](/media/screencast-trailmaking.gif)
