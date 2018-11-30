# Installing the Experiments

## Setting up Expyriment

Firstly to use any of the experiments provided here, you need to have python installed and running on your computer, and then you need to install expyriment as explained [here](https://www.expyriment.org/#installation).


### On an Android Device

Expyriment has a dedicated Android application which can be obtained from [here](https://github.com/expyriment/expyriment-android-runtime), which also contains instructions on how to install/start experiments.

However, I recommend to use a recent recompilation of the Android application which I have made that can be downloaded from [here](https://my.pcloud.com/publink/show?code=XZY8sM7ZNqcmeCdh2Qb6XASUIcPxSHj8gdiX);
it differs particularly in the size of that start menu, which in the original distribution is very small as it was made when android devices still largely had low DPI screens.
Note that this is not an officially supported version of the expyriment app for android.

## Preparing the Experiments

To use experiments, download from the [release page of this repository](https://github.com/mbroedl/cognitive-tasks-for-expyriment/releases), extract the folder where you want it to be, configure the config.conf and test the experiment a few times to make sure everything works.

On android devices, you need to put them in a folder called _expyriment_ on the root of your internal or external storage, for example in the folder `...sd-card/expyriment/digitspan/`.

## Starting Experiments

To run the experiment, you may be able to double click it on Windows, but otherwise you can open a command line and use a command such as `python C:\path\to\the\experiment.py` should work on all platforms.
On android you start the expyriment app an should be able to select the experiment.
