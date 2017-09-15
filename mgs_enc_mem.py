#!/usr/bin/env python2

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, core, data, logging, gui
import datetime
import glob
from mgs_task import shuf_for_ntrials, replace_img

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


## settings
# trials using trialHandler and list of dicts
ntrials=10
possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
allimages=glob.glob('img_circle/*png')

positions=shuf_for_ntrials(possiblepos,ntrials)
imgfiles = shuf_for_ntrials( allimages, ntrials)



## initialize

stimList = [  {'imgfile': imgfiles[i], 'horz': positions[i]   } for i in range(ntrials) ]
trials = data.TrialHandler(stimList,1,extraInfo ={'subjid': subjid, 'epoch': seconds})

#win = visual.Window([400,400],screen=0)
#win = visual.Window(fullscr=True)
win = visual.Window([1600,900])

img = visual.ImageStim(win,name="imgdot") #,AutoDraw=False)

# could have just one and change the color
iti_fix = visual.TextStim(win, text='+',name='iti_fixation',color='white')
isi_fix = visual.TextStim(win, text='+',name='isi_fixation',color='yellow')
trg_fix = visual.TextStim(win, text='+',name='trg_fixation',color='red')


def trial(imgfile,horz,iti): 
    trg_fix.draw(); win.flip(); core.wait(0.5)
    replace_img(img,imgfile,horz,.05); win.flip(); core.wait(.5) 
    isi_fix.draw(); win.flip(); core.wait(0.5)
    win.flip(); core.wait(.5)
    iti_fix.draw(); win.flip(); logging.flush(); core.wait(iti)

## run
for t in trials:
    trial(t['imgfile'],t['horz'],1.0)

win.close()
