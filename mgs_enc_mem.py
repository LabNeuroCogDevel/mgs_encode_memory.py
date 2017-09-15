#!/usr/bin/env python2


# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from psychopy import visual, core, data
from psychopy import logging
from __future__ import division
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
  # are we off the left side of the screen?
  #if   horzpos - halfimgsize < 0 : horz = halfimgsize/float(sw)
  #elif horzpos + halfimgsize > sw: horz = (sw -halfimgsize)/float(sw)
  if   horzpos - halfimgsize < 0 : horz = halfimgsize*2/float(sw) - 1
  elif horzpos + halfimgsize > sw: horz = (sw -halfimgsize)*2/float(sw) -1
  # set
  img.pos=(horz,0)

  ## draw
  img.draw()

## initialize
img = visual.ImageStim(win,name="imgdot") #,AutoDraw=False)

iti_fix = visual.TextStim(win, text='+',name='iti_fixation',color='white')
isi_fix = visual.TextStim(win, text='+',name='isi_fixation',color='yellow')
trg_fix = visual.TextStim(win, text='+',name='trg_fixation',color='red')


## run
def trial(imgfile,horz): 
    trg_fix.draw(); win.flip(); core.wait(0.5)
    replace_img(img,imgfile,horz,.15); win.flip(); core.wait(.5) 
    isi_fix.draw(); win.flip(); core.wait(0.5)
    win.flip(); core.wait(.5)
    iti_fix.draw(); win.flip(); core.wait(1.0)

trial("img_circle/winter.01.png",-.25)
trial("img_circle/mountain.01.png",-.75)
