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
from mgs_task import mgsTask, response_should_be, \
                     getInfoFromDataPath, imagedf_to_novel
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# where do we store data?
pkl_glb = os.path.join('subj_info', '*', '*', 'runs_info.pkl')
# what keys do we use?
accept_keys = {'known': '1',
               'maybeknown': '2',
               'maybeunknown': '3',
               'unknown': '4',
               'Left': '1',
               'NearLeft': '2',
               'NearRight': '3',
               'Right': '4',
               'oops': '5'}

# list all subject pickle files.
# sort by modification date
# used in dropdown dialog
allsubjs = sorted(glob.glob(pkl_glb), key=lambda x: -os.path.getmtime(x))
settings = {'recall_from': allsubjs, 'fullscreen': True,
            'instructions': True, 'lastrun': 3}

# --- test vs actual settings
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    iscodetest = True
    from psychopy.hardware.emulator import ResponseEmulator
    import random
    import gc
    # no instructions, pick first (in time) data file
    settings = {'recall_from': allsubjs[-1],
                'fullscreen': False,
                'instructions': False,
                'lastrun': 3}
    # clear the get ready screen
    r = ResponseEmulator([(5, 'space')])
    r.start()
else:
    iscodetest = False
    box = gui.DlgFromDict(settings)
    # exit if we dont hit okay
    if not box.OK:
        sys.exit(1)

# read in and parse
pckl = settings['recall_from']
datadir = os.path.dirname(pckl)
(subjid, tasktype, imgset, timepoint) = getInfoFromDataPath(datadir)

# load run info
with open(pckl, 'rU') as p:
    print(pckl)
    run_data = pickle.load(p)

# select what we've seen 
# put all runs together
lastrunidx = settings['lastrun']
seendf = pd.concat(run_data['run_timing'][0:lastrunidx])
	
# --- pick some novel stims --
imdf = run_data['imagedf']
# but remove images we haven't seen (but should have)
if(settings['lastrun'] < len(run_data['run_timing']) ):
	actuallysaw = pd.unique(seendf['imgfile'])
	unsee = [x not in actuallysaw for x in imdf['imgfile'] ]
	imdf.loc[unsee,'used'] = False

# from that, make a novelimg dataset
# with columns that match 
novelimg = imagedf_to_novel(imdf)


# get just the images and their side
seendf = seendf[seendf.imgtype != "None"][['side', 'imgfile', 'imgtype']]
# convert side to position (-1 '*Left', 1 if '*Right')
seendf['pos'] = [('Left' in x) * -1 + ('Right' in x)*1 for x in seendf['side']]
# combine them
trialdf = pd.concat([seendf[['imgfile', 'pos', 'imgtype']],
                     novelimg[['imgfile', 'pos', 'imgtype']]]).\
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
task.init_recall_side()

if settings['instructions']:
    task.recall_instructions()

# wait to start -- space or escape key
blockstarttime = task.wait_for_scanner(['space', 'escape'], 'ready?')

# # run recall quiz trials
# blocktimer.reset()
for t in recall_trials:
    print("correct keys: %s" % list(t['corkeys']))
    if iscodetest:
        resp = random.randint(1, 4)
        if resp <= 2:
            resparr = [(.5, resp),
                       (.75, random.randint(1, 4))]
        else:
            resparr = [(1, resp)]
        gc.collect()
        print("responding: %s" % resparr)
        r = ResponseEmulator(resparr)
        r.start()
    (keypresses, rts) = task.recall_trial(t['imgfile'])

    grade = [expect == given
             for expect, given in zip(t['corkeys'], keypresses)]
    # add key and rt
    recall_trials.addData('know_key', keypresses[0])
    recall_trials.addData('dir_key', keypresses[1])
    recall_trials.addData('know_rt', rts[0])
    recall_trials.addData('dir_rt', rts[1])
    print("%s %s %s %s" % (t['imgtype'], keypresses, grade, t['imgfile']))
    # finish with iti
    task.run_iti(.5)

# save results to recall.csv inside datadir
saveas = os.path.join(datadir, 'recall_%s.csv' % seconds)
recall_trials.data.to_csv(saveas)
print('saved %s' % saveas)
task.wait_for_scanner(['space'], 'Finished!')
task.win.close()
