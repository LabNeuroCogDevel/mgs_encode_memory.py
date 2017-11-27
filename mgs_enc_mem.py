#!/usr/bin/env python2
# -*- py-which-shell: "python2"; -*-

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, core, data, logging, gui  # , event
import datetime
import sys
import os
from mgs_task import mgsTask, gen_run_info, replace_img, take_screenshot, wait_until
# from mgs_task import *

# subjnum='0'; win = visual.Window([800,600]); task = mgsTask(win)

# paths are relative to this script
os.chdir(os.path.dirname(os.path.realpath(__file__)))


# # get subj info
# we can use the command line
# or we can get a windowed dialog box
if (len(sys.argv) > 1):
    subjnum = sys.argv[1]
    start_runnum = 1
    show_instructions = True
else:
    box = gui.Dlg()
    box.addField("Subject ID:")
    box.addField("Run number:", 1)
    box.addField("instructions?", True)
    boxdata = box.show()
    if box.OK:
        subjnum = boxdata[0]
        start_runnum = int(boxdata[1])
        show_instructions = boxdata[2]
    else:
        sys.exit(1)

subjid = subjnum
# maybe we want to auto add date?
# + datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")

# # settings
run_total_time = 420
nruns = 4
# TODO check against traildf max

# what key does the scanner send on the start of a TR?
# ^, =, or esc
scannerTriggerKeys = ['asciicircum', 'equal', 'escape', '6']

# # trials using trialHandler and list of dicts
# possiblepos=[-1, 1, -.75, .75, -.5, .5]
# # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
# (sacc_images,novel_images) = image_sets()

# # put together for saccade trials
# C:\Users\Public\Desktop\Tasks\mgs_encode_memory.py\

# # paths
savepath = 'subj_info'
datadir = os.path.join(savepath, subjid)
logdir = os.path.join(datadir, 'log')
for thisoutdir in [savepath, datadir, logdir]:
    if not os.path.exists(thisoutdir):
        os.makedirs(thisoutdir)

# # get all_runs_info
# all_run_info = {'imagedf': imagedf, 'run_timing': run_timing }
all_runs_info = gen_run_info(nruns, datadir)

# this is probably unecessary
# accept_keys = {'known':'k', 'unknown': 'd', 'left':'d','right':'k', 'oops':'o'}
accept_keys = {'known': '2', 'unknown': '3',
               'left': '2', 'right': '3',
               'oops': '1'}

# # screen setup
# win = visual.Window([400,400],screen=0)
# win = visual.Window(fullscr=True)
win = visual.Window([800, 600])
win.winHandle.activate()  # make sure the display window has focus
win.mouseVisible = False  # and that we don't see the mouse

task = mgsTask(win, accept_keys)


# # instructions
# OR hack to have somthing in image
#    incase we start with a 'None' null image trial
#    (instructions would do this)
if show_instructions:
    task.sacc_instructions()
else:
    replace_img(task.img, 'img/example.png', 1, task.imgratsize)
    win.flip()
    win.flip()

# take screenshots:
# takeshots="20171101"
takeshots = None

for runi in range(start_runnum-1, nruns):
    run = runi + 1
    print("### run %d" % run)
    trialdf = all_runs_info['run_timing'][runi]

    seconds = datetime.datetime.strftime(datetime.datetime.now(), "%H%M%S")

    # # logging
    logfilename = "info_%s_%d_%s.log" % (subjid, run, seconds)
    logfile = os.path.join(logdir, logfilename)
    lastLog = logging.LogFile(logfile, level=logging.INFO, filemode='w')
    logging.log(level=logging.INFO,
                msg='run %s, loading at epoch %s' % (run, seconds))
    logging.flush()  # when its okay to write

    # trial settings and timing
    sacc_trials = data.TrialHandler2(
                    trialdf.T.to_dict().values(),
                    1,
                    method='sequential',
                    extraInfo={'subjid': subjid,
                               'epoch': seconds,
                               })

    # # run saccade trials
    # blockstarttime=core.getTime()
    blockstarttime = task.wait_for_scanner(scannerTriggerKeys)
    logging.log(level=logging.INFO,
                msg='scanner trigger recieved at %d' % blockstarttime)

    # for all trials in this run
    for t in sacc_trials:
        # run the trial
        task.sacc_trial(t, blockstarttime, takeshots=takeshots, logh=logging)
        # then put up the iti cross
        task.run_iti()
        # and take a screenshot if we want it
        if takeshots:
            take_screenshot(win, takeshots + '_05_iti')
            break

    # finish up
    task.run_iti()

    savefile_csv = '%s_%d_view.csv' % (subjid, run)
    savefile_csv_path = os.path.join(datadir, savefile_csv)
    print('saving %s' % savefile_csv_path)
    sacc_trials.data.to_csv(savefile_csv_path)

    thisendtime = run_total_time + blockstarttime
    print("running to end of time (%.02f, actual %.02f)" %
          (run_total_time, thisendtime))
    wait_until(thisendtime)
    task.run_end(run, nruns)
    logging.flush()

win.close()

