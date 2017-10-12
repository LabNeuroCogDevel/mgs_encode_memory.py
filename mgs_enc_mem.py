#!/usr/bin/env python2

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, core, data, logging, gui, event
import datetime
import glob, re, math, numpy,sys,os
# del sys.modules['mgs_task'];
from mgs_task import *
#subjnum='0'; win = visual.Window([800,600]); task = mgsTask(win)

os.chdir( os.path.dirname(os.path.realpath(__file__) ) )


## get subj info
if (len(sys.argv)>1):
    subjnum=sys.argv[1]
else:
    box = gui.Dlg()
    box.addField("Subject ID:")
    box.show()
    subjnum=box.data[0]

subjid=subjnum + datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")
seconds=datetime.datetime.strftime(datetime.datetime.now(),"%H%M%S")


## logging
lastLog = logging.LogFile("info_%s_%s.log"%(subjid,seconds), level=logging.INFO, filemode='w')
logging.log(level=logging.INFO, msg='starting at %s'%core.Clock())
logging.flush() # when its okay to write
# timing
blocktimer = core.Clock()


## settings
# trials using trialHandler and list of dicts
possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
(sacc_images,novel_images) = image_sets()

## put together for saccade trials
# C:\Users\Public\Desktop\Tasks\mgs_encode_memory.py\
sacc_stimList= gen_stimlist(sacc_images,possiblepos,'stims\example_00001_')
sacc_trials = data.TrialHandler2(sacc_stimList,1,method='sequential',extraInfo ={'subjid': subjid, 'epoch': seconds})

if( any(numpy.diff([x['01_cue'] for x in sacc_stimList ]) < 0 ) ):
    raise Exception('target times are not monotonicly increasing! bad timing!')

## recall quiz setup
# unique image position: for quiz later
img_pos = set([ (x['imgfile'],x['horz']) for x in sacc_stimList ])

nrecall=len(img_pos)
nquiz=len(novel_images)
novel_pos = set([ (x,float("nan")) for x in novel_images ] )
img_pos_and_novel = list(novel_pos | img_pos) 
numpy.random.shuffle(img_pos_and_novel)


#accept_keys = {'known':'k', 'unknown': 'd', 'left':'d','right':'k', 'oops':'o' }
accept_keys = {'known':'2', 'unknown': '3', 'left':'2','right':'3', 'oops':'1' }


recall_stim = [ { 'imgfile': img,'pos': pos,'corkeys': response_should_be(pos,accept_keys) } for img,pos in img_pos_and_novel ]
recall_trials = data.TrialHandler2(recall_stim,1,extraInfo ={'subjid': subjid, 'epoch': seconds})


## screen setup
#win = visual.Window([400,400],screen=0)
win = visual.Window(fullscr=True)
#win = visual.Window([800,600])
win.winHandle.activate() # make sure the display window has focus
win.mouseVisible=False # and that we dont see the mouse

task = mgsTask(win,accept_keys)

## instructions
task.sacc_instructions()

## run saccade trials
#blockstarttime=core.getTime()
blockstarttime=task.wait_for_scanner(['asciicircum','equal','escape','6']) # ^, =, or esc
for t in sacc_trials:
    trialstarttime=blockstarttime + t['01_cue']
    mgson=blockstarttime + t['02_mgs']
    delaytime=mgson-trialstarttime-1.5*2

    print("")
    print("block idea,cur time, will launch @, diff(remaning iti)")
    print("%f,%f,%f,%f"%(t['01_cue'],core.getTime(), trialstarttime, trialstarttime-core.getTime()))
    print("delay time: %.2f"%(delaytime))

    task.sacc_trial(t['imgfile'],t['horz'],trialstarttime,mgson)
    sacc_trials.addData('startTime',trialstarttime)
    sacc_trials.addData('mgson',mgson)
    sacc_trials.addData('delaylen',delaytime)
    task.run_iti() #.5)

#sacc_trials.saveAsText(subjid + '_view.txt')
sacc_trials.data.to_csv(subjid + '_view.csv')


print("running 12 second iti")
task.run_iti(12)

## run recall quiz trials
#blocktimer.reset()

# this should work but does not!
#recall_trails.data.to_csv(subjid + '_recall.csv')

logging.flush()
# TODO save recall_trials and sacc_trials
win.close()
