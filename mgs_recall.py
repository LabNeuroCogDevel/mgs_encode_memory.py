#!/usr/bin/env python2
# -*- elpy-rpc-python-command: "python"; -*-
# -*- py-which-shell: "python2"; -*-
# -*- elpy-use-ipython: "ipython"; -*-
# (setq elpy-rpc-python-command "python")  (setq py-which-shell "python2") 
# (setq elpy-use-ipython "ipython")
from __future__ import division
from psychopy import visual, data, gui
import datetime
import glob
import os
import sys
from mgs_task import mgsTask, response_should_be, \
                     getInfoFromDataPath, \
                     recallFromPickle, host_tasktype, vdate_str, \
                     create_window

os.chdir(os.path.dirname(os.path.realpath(__file__)))

# where do we store data?
# like: subj_info/abcd/01/eeg_B_20180221/runs_info.pkl

pkl_glb = [
           # put all macOS volume possiblities first
           os.path.join('/Volumes', '*','Data','1*','*', '*', '*','runs_info.pkl'),
           os.path.join('/Volumes', '*','Data','1*', '*', '*','runs_info.pkl'),
           os.path.join('/Volumes', '*', '*','subj_info','*', '*', '*','runs_info.pkl'),
           os.path.join('/Volumes', '*', 'subj_info','*', '*', '*', 'runs_info.pkl'),
           # lastly check the curent (script) folder (for presentaiton on MR computer)
           os.path.join('subj_info', '*', '*', '*', 'runs_info.pkl')#,
           #os.path.join('/Volumes', '*', '*', 'runs_info.pkl')
           ]
# what keys do we use?
accept_keys = {'known': '1',
               'maybeknown': '2',
               'maybeunknown': '9',
               'unknown': '0',
               'Left': '1',
               'NearLeft': '2',
               'NearRight': '9',
               'Right': '0',
               'oops': '5'}

# list all subject pickle files.
# sort by modification date
# used in dropdown dialog

nruns_opt = {'mri': 3, 'eeg': 4, 'test': 2, 'unkown': 3, 'behave': 2}

# glob all the paths provided, flatten, order by modified time
globs = [ glob.glob(x) for x in pkl_glb ];
globs_flat = [item for sublist in globs for item in sublist]
allsubjs = sorted(globs_flat, key=lambda x: -os.path.getmtime(x))

settings = {'recall_from': allsubjs,
            'fullscreen': True,
            'instructions': True,
            'firstrun': 1,
            'lastrun': nruns_opt[host_tasktype()]}

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

trialdf = recallFromPickle(pckl, settings['lastrun'], settings['firstrun']-1)

# set correct keys and format for trialhandler
trialdict = trialdf.reset_index().T.to_dict().values()
trialdict = [
        dict(x.items() +
             {'corkeys': response_should_be(x['pos'], accept_keys)}.items())
        for x in trialdict]

seconds = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S")

extraInfo = {'subjid': subjid, 'epoch': seconds}
recall_trials = data.TrialHandler2(trialdict, 1, extraInfo=extraInfo)


# # screen setup
win = create_window(settings['fullscreen'])

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
    if not os.path.exists(t['imgfile']):
        t['imgfile'] = t['imgfile'].replace("\\", "/")
    (keypresses, rts) = task.recall_trial(t['imgfile'])

    grade = [expect == given
             for expect, given in zip(t['corkeys'], keypresses)]

    # did we get the correct known/unknown
    trialscore = 0

    # ---- scores ----
    # -- didn't see
    # 1   = said saw (but didn't)
    # 101 = said maybe didn't
    # 201 = confidently correct
    # --- did see
    # 0 = said didn't
    # 100 = maybe known
    # 200 = confidently correct
    # -- side
    # +5  = correct side    (105, 205)
    # +15 = exactly correct (115,215)

    # we should have respond that we knew the image
    if t['pos'] in [-1, -.5, .5, 1]:
        if keypresses[0] == accept_keys['known']:
            trialscore += 200
        elif keypresses[0] == accept_keys['maybeknown']:
            trialscore += 100

        # did we get the side right (add 5)
        leftkeys = [accept_keys['Left'], accept_keys['NearLeft']]
        rightkeys = [accept_keys['Right'], accept_keys['NearRight']]
        if keypresses[1] in leftkeys and t['corkeys'][1] in leftkeys:
            trialscore += 5
        if keypresses[1] in rightkeys and t['corkeys'][1] in rightkeys:
            trialscore += 5

        # up to 15 if correct side and correct near/far
        if keypresses[1] == t['corkeys'][1]:
            trialscore += 10
    # did not see image
    else:
        if keypresses[0] == accept_keys['unknown']:
            trialscore += 201
        elif keypresses[0] == accept_keys['maybeunknown']:
            trialscore += 101
        # we said we saw an image but we didn't
        # give one point to distinguish from saw but said no (score=0)
        else:
            trialscore += 1

    # add key and rt
    recall_trials.addData('score', trialscore)
    recall_trials.addData('know_key', keypresses[0])
    recall_trials.addData('dir_key', keypresses[1])
    recall_trials.addData('know_rt', rts[0])
    recall_trials.addData('dir_rt', rts[1])
    print("%s %s %s %s %s %s" %
          (t['imgtype'], keypresses, grade, trialscore,
           t['pos'], t['imgfile']))
    # finish with iti
    task.run_iti(.5)

task.wait_for_scanner(['space'], 'Finished!')
task.win.close()

# save results to recall.csv inside datadir
csvfilename = "_".join([subjid, vdate_str(), tasktype,
                        str(timepoint),
                        'recall-%s_%s.csv' % (imgset, seconds)])
saveas = os.path.join(datadir, csvfilename)

# save file in data directory. might be read only :(
isSaved = False
while not isSaved:
    try:
        recall_trials.data.to_csv(saveas)
        isSaved = True
    except:
        saveas = gui.fileSaveDlg(initFilePath='/Users/danielamejia/Desktop/', initFileName=csvfilename, prompt=u'Data is readonly, save where?')
print('saved %s' % saveas)


