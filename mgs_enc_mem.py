#!/usr/bin/env python2

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, core, data, logging, gui, event
import datetime
import glob, re, math, numpy
from mgs_task import *

## get subj info
box = gui.Dlg()
box.addField("Subject ID:")
box.show()
subjid=box.data[0] + datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")
seconds=datetime.datetime.strftime(datetime.datetime.now(),"%s")


## logging
lastLog = logging.LogFile("info_%s_%s.log"%(subjid,seconds), level=logging.INFO, filemode='w')
logging.log(level=logging.INFO, msg='starting at %s'%core.Clock())
logging.flush() # when its okay to write
# timing
timer = core.Clock()
blocktimer = core.Clock()


## settings
# trials using trialHandler and list of dicts
n_sacc_trials=10
possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
allimages=glob.glob('img_circle/*png')

## break images into saccade images and novel (for memory quiz)
novelfile=re.compile('.*\.01\..*') # any .01. image
sacc_images = [ x for x in allimages if not novelfile.match(x) ]
novel_images = [ x for x in allimages if novelfile.match(x) ]

## put together for saccade trials
sacc_stimList= gen_stimlist(sacc_images,possiblepos,n_sacc_trials)
# unique image position: for quiz later
img_pos = set([ (x['imgfile'],x['horz']) for x in sacc_stimList ])

sacc_trials = data.TrialHandler2(sacc_stimList,1,extraInfo ={'subjid': subjid, 'epoch': seconds})

## recall quiz setup
nrecall=len(img_pos)
nquiz=len(novel_images)
novel_pos = set([ (x,float("nan")) for x in novel_images ] )
img_pos_and_novel = list(novel_pos | img_pos) 
numpy.random.shuffle(img_pos_and_novel)


accept_keys = {'known':'k', 'unknown': 'd', 'left':'d','right':'k', 'oops':'o' }


recall_stim = [ { 'imgfile': img,'pos': pos,'corkeys': response_should_be(pos,accept_keys) } for img,pos in img_pos_and_novel ]
recall_trials = data.TrialHandler2(recall_stim,1,extraInfo ={'subjid': subjid, 'epoch': seconds})


## screen setup
#win = visual.Window([400,400],screen=0)
#win = visual.Window(fullscr=True)
win = visual.Window([800,600])

task = mgsTask(win,accept_keys)

## run saccade trials
blocktimer.reset()
for t in sacc_trials:
    trialstarttime=blocktimer.getTime()
    task.sacc_trial(t['imgfile'],t['horz'])
    sacc_trials.addData('startTime',trialstarttime)
    task.run_iti(.5)

## run recall quiz trials
#blocktimer.reset()
for t in recall_trials:
    (keypresses,rts) = task.recall_trial(t['imgfile'])
    grade = [ expect==given for expect,given in zip( t['corkeys'], keypresses ) ]
    # add key and rt
    recall_trials.addData('know_key',keypresses[0])
    recall_trials.addData('dir_key',keypresses[1])
    recall_trials.addData('know_rt',rts[0])
    recall_trials.addData('dir_rt',rts[1])
    # finish with iti
    task.run_iti(.5)

win.close()
