#!/usr/bin/env python2

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, core, data, logging, gui
import datetime
import glob, re, math
from mgs_task import shuf_for_ntrials, replace_img, gen_stimlist

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
n_sacc_trials=10
possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
allimages=glob.glob('img_circle/*png')

## break images into saccade images and novel (for memory quiz)
novelfile=re.compile('.*\.01\..*') # any .01. image
sacc_images = [ x for x in allimages if not novelfile.match(x) ]
novel_images = [ x for x in allimages if novelfile.match(x) ]

sacc_stimList= gen_stimlist(sacc_images,possiblepos,n_sacc_trials)
# unique image position: for quiz later
img_pos = set([ (x['imgfile'],x['horz']) for x in sacc_stimList ])

sacc_trials = data.TrialHandler(sacc_stimList,1,extraInfo ={'subjid': subjid, 'epoch': seconds})

### recall quiz setup
nrecall=len(img_pos)
nquiz=len(novel_images)
novel_pos = set([ (x,float("nan")) for x in novel_images ] )
img_pos_and_novel = list(novel_pos | img_pos) 
numpy.random.shuffle(img_pos_and_novel)

def response_should_be(pos):
    known='K';unkown='D';
    left ='D';right ='K';oops='O'
    
    if(math.isnan(pos )): return( (unkown,oops) )
    elif( pos < 0): return(known,left)
    elif( pos > 0): return(known,right)
    else: raise ValueError('bad pos?! how!?')

recall_stim = [ { 'imgfile': img,'pos': pos,'keys': response_should_be(pos) } for img,pos in img_pos_and_novel ]
recall_trials = data.TrailHandler(reacall_stim,1,extraInfo ={'subjid': subjid, 'epoch': seconds})
### screen setup

#win = visual.Window([400,400],screen=0)
#win = visual.Window(fullscr=True)
win = visual.Window([800,600])

img = visual.ImageStim(win,name="imgdot") #,AutoDraw=False)

# could have just one and change the color
iti_fix = visual.TextStim(win, text='+',name='iti_fixation',color='white')
isi_fix = visual.TextStim(win, text='+',name='isi_fixation',color='yellow')
trg_fix = visual.TextStim(win, text='+',name='trg_fixation',color='red')

## for quiz
text_KU = visual.TextStim(win, text='known or unknown',name='KnownUnknown',color='white',pos=(0,-.75))
text_LR = visual.TextStim(win, text='left or right',name='LeftRight',color='white',pos=(0,-.75))

def sacc_trial(imgfile,horz,iti): 
    trg_fix.draw(); win.flip(); core.wait(0.5)
    replace_img(img,imgfile,horz,.05); win.flip(); core.wait(.5) 
    isi_fix.draw(); win.flip(); core.wait(0.5)
    win.flip(); core.wait(.5)
    iti_fix.draw(); win.flip(); logging.flush(); core.wait(iti)

def sacc_trial(imgfile,keys,iti=.5): 
    replace_img(img,imgfile,0,.25);text_KU.draw(); win.flip();
    # TODO key catpure
    core.wait(1)
    # if report known
    replace_img(img,imgfile,0,.25);text_LR.draw(); win.flip();
    core.wait(1)

    iti_fix.draw(); win.flip(); logging.flush(); core.wait(iti)

## run
for t in sacc_trials:
    sacc_trial(t['imgfile'],t['horz'],1.0)

## recall
for t in recall_trials:
    trial(t['imgfile'],t['horz'],1.0)

win.close()
