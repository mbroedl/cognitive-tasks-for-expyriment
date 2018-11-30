# Translating Experiments
If you would like to use experiments in a different language or change the display messages, look at the _i18n.conf_ file distributed with each experiment.
Each block denoted by square brackets corresponds to one language, the `[en]` block has English instructions and is the default.

If you would like to change the language of your experiment, please make sure the language is available in the _i18n.conf_ and adjust the `language =` value in the `[GENERAL]` section of the configuration file _config.conf_ to the name of that block (e.g. `language = en` for English).


## Changing Instructions
In case you would like to change any instructions, make sure to preserve the message keys (i.e. the part before the `=`-sign) and only change what is written afterwards.

If you would like to add an instruction where there is currently none, please add [an issue](https://github.com/mbroedl/cognitive-tasks-for-expyriment/issues) on GitHub;
if you would like to remove an instruction completely, please use the value `SKIP` (e.g. `thanks = SKIP`) but do not delete it.

<!--
If you would like to add variables to your instructions, you may do so by putting the name of the variable into curly braces.
The name of the variable should be one of those that you can use for logging data, but excludes aggregation and filters.
<!-- TODO implement! -->


## Adding a Translation
To add a translation to an existing experiment, please copy the whole `[en]`-section in `i18n.conf` within the same file, and change the block name in brackets to the language code of your translation.
Then you can translate all items to the according language; make sure to preserve the key before the `=`-sign and make sure to not accidentally delete any key as otherwise the experiment may crash.


### Contributing Translations
If you would like your translation to be available to other users, please create a pull request or [an issue](https://github.com/mbroedl/cognitive-tasks-for-expyriment/issues) on the GitHub repository with the translated instructions.
For a guide on how to do this, see [here](https://help.github.com/articles/creating-an-issue/).
