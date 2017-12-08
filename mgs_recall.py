#!/usr/bin/env python2
# -*- elpy-rpc-python-command: "python"; -*-
# -*- py-which-shell: "python2"; -*-
# -*- elpy-use-ipython: "ipython"; -*-
# (setq elpy-rpc-python-command "python")  (setq py-which-shell "python2") 
# (setq elpy-use-ipython "ipython")
from __future__ import division
from psychopy import visual, core, data, logging, gui, event
import datetime
import pickle
import pandas as pd
import glob
import os
import sys
from mgs_task import mgsTask, response_should_be, getInfoFromDataPath
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# where do we store data?
pkl_glb = os.path.join('subj_info', '*', '*', 'runs_info.pkl')
# what keys do we use?
accept_keys = {'known': '2', 'unknown': '3',
               'left': '2', 'right': '3',
               'oops': '1'}

# list all subject pickle files.
# sort by modification date
# used in dropdown dialog
allsubjs = sorted(glob.glob(pkl_glb), key=lambda x: -os.path.getmtime(x) )
settings = {'recall_from': allsubjs, 'fullscreen':True, 'instructions': True}
box = gui.DlgFromDict(settings)

# exit if we dont hit okay
if not box.OK:
    sys.exit(1)

# read in and parse
pckl = settings['recall_from']
datadir = os.path.dirname(pckl)
(subjid, tasktype, imgset, timepoint) = getInfoFromDataPath(datadir)

# load run info
with open(pckl, 'rb') as p:
    run_data = pickle.load(p)


# pick some novel stims
imdf = run_data['imagedf']
# TODO, subset natural and man made?
nused = imdf[imdf.used].\
        groupby('imgtype').\
        aggregate({'used': lambda x: x.shape[0]})
# resample from unused each type as needed
novelimg = pd.concat([
    imdf[(imdf.used == False) &
         (imdf.imgtype == r[0])].
    sample(r[1].used)
    for r in nused.iterrows()])
# add empty position
novelimg['pos'] = float("nan")

# # select what we've seen
# put all runs together
seendf = pd.concat(run_data['run_timing'])
# get just the images and their side
seendf = seendf[seendf.imgtype != "None"][['side', 'imgfile','imgtype']]
# convert side to position (-1 '*Left', 1 if '*Right')
seendf['pos'] = [('Left' in x) * -1 + ('Right' in x)*1 for x in seendf['side']]
# combine them
trialdf = pd.concat([seendf[['imgfile', 'pos','imgtype']],
                     novelimg[['imgfile', 'pos','imgtype']]]).\
                     sample(frac=1)

# set correct keys and format for trialhandler
trialdict = trialdf.T.to_dict().values()
trialdict = [
        dict(x.items() +
            {'corkeys': response_should_be(x['pos'], accept_keys)}.items())
        for x in trialdict]

seconds = datetime.datetime.strftime(datetime.datetime.now(), "%Y%M%d%H%M%S")

extraInfo = {'subjid': subjid, 'epoch': seconds}
recall_trials = data.TrialHandler2(trialdict, 1, extraInfo=extraInfo)


# # screen setup
if settings['fullscreen']:
    win = visual.Window(fullscr=True)
else:
    win = visual.Window([400, 400], screen=0)
# win = visual.Window(fullscr=True)

# win settings
win.winHandle.activate()  # make sure the display window has focus
win.mouseVisible = False  # and that we dont see the mouse

# task class
task = mgsTask(win, accept_keys)

if settings['instructions']:
    task.recall_instructions()

# wait to start -- space or escape key
blockstarttime = task.wait_for_scanner(['space', 'escape'], 'ready?')

# # run recall quiz trials
# blocktimer.reset()
for t in recall_trials:
    (keypresses, rts) = task.recall_trial(t['imgfile'])
    grade = [expect == given
             for expect, given in zip(t['corkeys'], keypresses)]
    # add key and rt
    recall_trials.addData('know_key', keypresses[0])
    recall_trials.addData('dir_key', keypresses[1])
    recall_trials.addData('know_rt', rts[0])
    recall_trials.addData('dir_rt', rts[1])
    # finish with iti
    task.run_iti(.5)

# save results to recall.csv inside datadir
saveas = os.path.join(datadir, 'recall_%s.csv' % seconds)
recall_trials.data.to_csv(saveas)
