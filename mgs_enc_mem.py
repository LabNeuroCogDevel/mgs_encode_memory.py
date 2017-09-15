#!/usr/bin/env python


# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py

from psychopy import visual, core, data
from psychopy import logging
import numpy,math,numpy.matlib,random,numpy.random

def shuf_for_ntrials(vec,ntrials):
  n=int(math.ceil( float(ntrials)/len(vec) ))
  mat=numpy.matlib.repmat(vec,1, n).flatten()
  numpy.random.shuffle(mat)
  return(mat)


## logging
lastLog = logging.LogFile("info.log", level=logging.INFO, filemode='w')
logging.log(level=logging.INFO, msg='starting at %s'%core.Clock())
logging.flush() # when its okay to write

## setup
win = visual.Window([400,400],screen=0)

# trials using trialHandler and list of dicts
ntrials=10
possiblepos=[0,.25,.75,1]
positions=shuf_for_ntrials(possiblepos,ntrials)

stimList = [  {'isi': .5, 'imgno': i, 'horz': positions[i]   } for i in range(ntrials) ]
trials = data.TrialHandler(stimList,10,extraInfo ={})


## run
message = visual.TextStim(win, text='hello')
message.setAutoDraw(True)  # automatically draw every frame
win.flip()
core.wait(2.0)
message.setText('world')  # change properties of existing stim

img = visual.ImageStim(win,'img_circle/winter.02.png')
img.setAutoDraw(False)
win.flip()
core.wait(2.0)
