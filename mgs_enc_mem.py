#!/usr/bin/env python2


# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, core, data, logging
import numpy,math,numpy.matlib,random,numpy.random
import glob

def shuf_for_ntrials(vec,ntrials):
  n=int(math.ceil( float(ntrials)/len(vec) ))
  mat=numpy.matlib.repmat(vec,1, n).flatten()
  numpy.random.shuffle(mat)
  return(mat[:ntrials])


## logging
lastLog = logging.LogFile("info.log", level=logging.INFO, filemode='w')
logging.log(level=logging.INFO, msg='starting at %s'%core.Clock())
logging.flush() # when its okay to write


# trials using trialHandler and list of dicts
ntrials=10
possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
positions=shuf_for_ntrials(possiblepos,ntrials)
imgfiles = shuf_for_ntrials( glob.glob('img_circle/*png'), ntrials)

stimList = [  {'imgfile': imgfiles[i], 'horz': positions[i]   } for i in range(ntrials) ]
trials = data.TrialHandler(stimList,1,extraInfo ={})


# we could  img.units='deg', but that might complicate testing on diff screens
def ratio(x,y,scale): return(float(x) * scale/float(y))
def replace_img(img,filename,horz,imgpercent=.04):
  # set image, get props
  img.image=filename
  (iw,ih) = img._origSize
  (sw,sh) = img.win.size
  
  # resize img
  scalew= ratio(sw,iw,imgpercent)
  #scaleh= ratio(sh,ih,imgpercent) 
  # scale evenly in relation to x-axis
  img.size=(scalew,scalew) 

  ## position
  horzpos=sw/2.0 * (1 + horz)
  halfimgsize=scalew*iw/2.0
  # are we partially off the screen? max edges perfect
  if   horzpos - halfimgsize < 0 : horz = halfimgsize*2/float(sw) - 1
  elif horzpos + halfimgsize > sw: horz = (sw -halfimgsize)*2/float(sw) -1
  # set
  img.pos=(horz,0)

  ## draw
  img.draw()

## initialize
#win = visual.Window([400,400],screen=0)
#win = visual.Window(fullscr=True)
win = visual.Window([1600,900])

img = visual.ImageStim(win,name="imgdot") #,AutoDraw=False)

iti_fix = visual.TextStim(win, text='+',name='iti_fixation',color='white')
isi_fix = visual.TextStim(win, text='+',name='isi_fixation',color='yellow')
trg_fix = visual.TextStim(win, text='+',name='trg_fixation',color='red')


## run
def trial(imgfile,horz,iti): 
    trg_fix.draw(); win.flip(); core.wait(0.5)
    replace_img(img,imgfile,horz,.05); win.flip(); core.wait(.5) 
    isi_fix.draw(); win.flip(); core.wait(0.5)
    win.flip(); core.wait(.5)
    iti_fix.draw(); win.flip(); logging.flush(); core.wait(iti)

for t in trials:
    trial(t['imgfile'],t['horz'],1.0)
