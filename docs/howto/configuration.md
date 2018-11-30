# Configuring the Experiments

Each experiment has one configuration file and one translation included.
These files can be modified to suit the demands of your research group on the experiment.
After each change of configuration, please make sure to test the experiments, as some values or missing configuration options might cause the experiment to crash.

Each _config.conf_ is built up from a number of sections, of which the sections `[GENERAL]`, `[DESIGN]`, and `[LOG]` are mandatory and the others are optional.
In the following sections, the purpose and generic use of each of these sections is described.


## [GENERAL]
This is the general configuration for this experiment.

Required options for each experiment:

```ini
# sets the language of the experiment to (in this case) English
# or any other language code specified in i18n.conf; for detailed
# information see the instructions on translating [required]
language = en
# defines whether the experiment requires a session id on top of
# a participant id; it will be automatically logged to all
# outputs and will be visible in the filenames of individual
# experiment outputs [required]
log_session = yes
```

Optional options for each experiment in this section.

```ini
# window size of the experiment, implies windowed mode as opposed
# to fullscreen; on android the experiment will still run in full
# screen but with less resolution [no default; e.g. 800, 600]
window_size =
# the following DPI settings are suggested to be set if you
# use mm, cm, or in to describe dimensions
# DPI is estimated in this order by
# (1) set dpi [no default]
dpi =
# (2) on android devices the DPI is read from the device
# (3) calculating the DPI by using window_size and
# screen_diagonal [no default; only works in full screen mode]
# [can be set in in or cm, e.g. 13.3in, 50cm]
screen_diagonal =
# (4) a fallback DPI when no device DPI could be identified
fallback_dpi = 96
```

Notes on `window_size`:
On old android devices you might encounter issues with performance.
To maintain the right sizes of stimuli, make sure to set the `dpi` yourself or to supply a value for `screen_diagonal`.
Also make sure to reduce the screen size proportionally, as boundaries are cropped;
so supplying a 16:10 window size to a 4:3 screen will not utilise the whole window and might result in unexpected results.

<!--
## [PRACTICE]
<!-- TODO -->

## [DESIGN]
The design section includes information about the general design of the experiment, such as the number of blocks or trials.
Information on the configuration settings are available in the respective documentation on each experiment.

## [APPEARANCE]
The appearance section includes information about the general appearance of the experiment, including colours or font sizes.
Information on experiment specific configuration settings are available in the respective documentation on each experiment.

<!--
## [ANDROID]
This section describes custom behaviour when the experiment is run on android devices.
<!-- TODO describe android-configuration + allow overwrite screen resolution and text scale -->

## [LOG]
In this section it is defined what variables should be logged and to which files they are logged, [see here](../logs/) for detailed information.

## [DEVELOPMENT]
This section is intended for development or exploration purposes.

- `active = (yes|no)` allows to enable [expyriment's development mode](https://docs.expyriment.org/expyriment.control.html?highlight=dev#expyriment.control.set_develop_mode) which will among others reduce waiting times, screen size, and to run the experiment in a window; only if this is enabled do any of the further settings have effect
- `log_all_variables = FILENAME.csv` : If this setting is present, all variables computed by the experiment are logged in alphabetical order for every trial to the file specified. This setting is useful for debug purposes.
