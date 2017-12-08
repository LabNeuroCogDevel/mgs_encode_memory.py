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
from mgs_task import mgsTask, response_should_be
os.chdir(os.path.dirname(os.path.realpath(__file__)))

accept_keys = {'known': '2', 'unknown': '3',
               'left': '2', 'right': '3',
               'oops': '1'}

# where do we store data?
pkl_glb = os.path.join('subj_info', '*', '*', 'runs_info.pkl')
allsubjs = glob.glob(pkl_glb)
pckl = allsubjs[2]
with open(pckl, 'rb') as p:
    run_data = pickle.load(p)

# TODO: pull from pckl or filename
subjid = 'test_2'

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
seendf = seendf[seendf.imgtype != "None"][['side', 'imgfile']]
# convert side to position (-1 '*Left', 1 if '*Right')
seendf['pos'] = [('Left' in x) * -1 + ('Right' in x)*1 for x in seendf['side']]
# combine them
trialdf = pd.concat([seendf[['imgfile', 'pos']],
                     novelimg[['imgfile', 'pos']]]).\
                     sample(frac=1)

# set correct keys and format for trialhandler
trialdict = trialdf.T.to_dict().values()
trialdict = [
        dict(x.items() +
            {'corkeys': response_should_be(x['pos'], accept_keys)}.items())
        for x in trialdict]

seconds = datetime.datetime.strftime(datetime.datetime.now(), "%H%M%S")

extraInfo = {'subjid': subjid, 'epoch': seconds}
recall_trials = data.TrialHandler2(trialdict, 1, extraInfo=extraInfo)


# # screen setup
win = visual.Window([400, 400], screen=0)
# win = visual.Window(fullscr=True)

# win settings
win.winHandle.activate()  # make sure the display window has focus
win.mouseVisible = False  # and that we dont see the mouse

# task class
task = mgsTask(win, accept_keys)

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

# this should work but does not!
recall_trials.data.to_csv(subjid + '_recall.csv')
