#!/usr/bin/env python2
from __future__ import division
from psychopy import visual, core, data, logging, gui, event
import datetime
import glob, re, math, numpy,sys,os
# del sys.modules['mgs_task'];
from mgs_task import *
os.chdir( os.path.dirname(os.path.realpath(__file__) ) )

possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
(sacc_images,novel_images) = image_sets()
seconds=datetime.datetime.strftime(datetime.datetime.now(),"%H%M%S")

# TODO: read this from saved file
subjnum='0'
subjid=subjnum + datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")
sacc_stimList= gen_stimlist(sacc_images,possiblepos,os.path.join('stims','example_00001_'))
sacc_trials = data.TrialHandler2(sacc_stimList,1,method='sequential',extraInfo ={'subjid': subjid, 'epoch': seconds})


## recall quiz setup
# unique image position: for quiz later
img_pos = set([ (x['imgfile'],x['horz']) for x in sacc_stimList ])

nrecall=len(img_pos)
nquiz=len(novel_images)
novel_pos = set([ (x,float("nan")) for x in novel_images ] )
img_pos_and_novel = list(novel_pos | img_pos) 

numpy.random.shuffle(img_pos_and_novel)
accept_keys = {'known':'2', 'unknown': '3', 'left':'2','right':'3', 'oops':'1' }
recall_stim = [ { 'imgfile': img,'pos': pos,'corkeys': response_should_be(pos,accept_keys) } for img,pos in img_pos_and_novel ]
recall_trials = data.TrialHandler2(recall_stim,1,extraInfo ={'subjid': subjid, 'epoch': seconds})


## screen setup
win = visual.Window([400,400],screen=0)
#win = visual.Window(fullscr=True)

# win settings
win.winHandle.activate() # make sure the display window has focus
win.mouseVisible=False # and that we dont see the mouse

# task class
task = mgsTask(win,accept_keys)

# wait to start
blockstarttime=task.wait_for_scanner(['asciicircum','equal','escape','6'],text='ready?') # ^, =, or esc

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

# this should work but does not!
recall_trails.data.to_csv(subjid + '_recall.csv')
