connect screen:
 hdmi on right port (not left!)
connect eyetracker: 
 sudo eyelink_network.bash

check ptb:
 "testDevices:

run
 ptb3-matlab
 mgs

ues sticker, postion eyes then start task
a on eyetracker
escape on matlab

copy files from:
subj_info/ieeg/99/99_A_20200123131713.mat

copy eye tracking from
http://100.1.1.1/




# TODO:
* send mgs position with `!v IAREA_RECTANGE` (see [video][https://youtu.be/NS1_lJUpWKU?t=1103])
* show video at start `PsychEyelinkDispatchCallback`
   http://psychtoolbox.org/docs/PsychEyelinkDispatchCallback
   https://github.com/Psychtoolbox-3/Psychtoolbox-3/blob/master/Psychtoolbox/PsychHardware/EyelinkToolbox/EyelinkBasic/PsychEyelinkDispatchCallback.m
   http://psychtoolbox.org/docs/Eyelink-ReadFromTracker
     - check distance -- show warning. show participant
     http://psychtoolbox.org/docs/Eyelink-ReadFromTracker
     http://psychtoolbox.org/docs/Eyelink-GetFloatDataRaw
     HMARKER is originally head target. but might have extra data
     - run drift correct
     http://psychtoolbox.org/docs/Eyelink-DriftCorrStart
* reduce trial length
