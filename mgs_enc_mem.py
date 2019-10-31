#!/usr/bin/env python2
# -*- py-which-shell: "python2"; -*-

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import data, logging, gui, core  # , event
import datetime  # set timepoint default, start time
import sys
import os
from mgs_task import mgsTask, gen_run_info, \
                     take_screenshot, wait_until, getSubjectDataPath, \
                     create_window
from showCal import showCal
from host_info import host_tasktype
# from mgs_task import *

# ---- settings -----
# -- host specific --
run_total_time = {'mri': 420, 'eeg': 358, 'test': 15,
                  'practice': 65, 'unknown': 420, 'behave': 240, 'ieeg': 358}
nruns_opt = {'mri': 3, 'eeg': 4, 'test': 2,
             'practice': 1, 'behave': 2, 'unknown': 3, 'ieeg': 4}
vert_offset_opt = {'mri': 0, 'eeg': 0, 'test': 0,
                   'practice': 0, 'unknown': 0,
                   'ieeg': 0,
                   'behave': 0}

record_video_opt = {'mri': True, 'eeg': False, 'test': False, 'ieeg': False,
                    'behave': False, 'practice': False, 'unknown': False}

calibration_opt = {'mri': False, 'eeg': False, 'test': False, 'ieeg': False,
                   'behave': True, 'practice': False, 'unknown': False}
usePP_opt = {'mri': False, 'eeg': True, 'test': False, 'ieeg': True,
             'behave': True, 'practice': False, 'unknown': False}

# what are we doing with the parallel port
ET_opts = {
        'mri': 'arrington',
        'unknown': 'arrington',
        'behave': 'ASL',
        'ieeg': 'pylink',
        'eeg': None,
        'practice': None, 'test': None}

# -- general settings --
mgsdur = 2  # this is tr locked for fmri
# TODO check against traildf max

# what key does the scanner send on the start of a TR?
# ^, =, or esc
scannerTriggerKeys = ['asciicircum', 'equal', 'escape', '6']

# paths are relative to this script
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# default settings
show_instructions = True
isfullscreen = True
subjnum = ''
imgset = 'A'
# 2018 is tp1
timepoint = datetime.datetime.now().year - 2017
getReadyMsg = 'Waiting for scanner (pulse trigger)'

# settings based on tasktype
host_type = host_tasktype()
default_type = host_type.tasktype
if default_type == 'unknown':
    print('unknown host, defaulting to mri')
    default_type = 'mri'

nruns = nruns_opt[default_type]
ET_type = ET_opts[default_type]
vertOffset = vert_offset_opt[default_type]
recVideo = record_video_opt[default_type]
calEyeScreen = calibration_opt[default_type]
midwayPause = False


# # different defaults for different computers
if default_type in ['eeg', 'ieeg']:
    scannerTriggerKeys = scannerTriggerKeys + ['space']
    getReadyMsg = 'Ready?'
    midwayPause = True
elif default_type == 'test':
    subjnum = 'test'
    show_instructions = False
    isfullscreen = False
    scannerTriggerKeys = scannerTriggerKeys + ['space']
    getReadyMsg = 'TESTING TESTING TESTING'
elif default_type == 'practice':
    scannerTriggerKeys = scannerTriggerKeys + ['space']
    getReadyMsg = 'Get Ready!'
    imgset = 'practice'
elif default_type == 'behave':
    scannerTriggerKeys = scannerTriggerKeys + ['space']
    getReadyMsg = 'Get Ready!'
    imgset = 'behave'
elif default_type == 'mri':
    pass
else:
    print('tasktype is "%s"! This should never happen' % default_type)

# compute date compenent of id
subjdateid = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")

# # get subj info
# we can use the command line
# or we can get a windowed dialog box
if (len(sys.argv) > 1):
    subjnum = sys.argv[1]
    start_runnum = 1 if len(sys.argv) <= 2 else int(sys.argv[2])
    from psychopy.hardware.emulator import ResponseEmulator
    print("sending trigger in 6 seconds")
    r = ResponseEmulator([(6, 'space'),    # advance trigger
                          (27, 'space')])  # finish
    r.start()

else:
    # NB. should consider 'gui.DlgFromDict(settings)' a la vgs_anti.py
    #     but cannot set default that way?
    # so instead we manually keep order pushing to box_key array
    box_key = []
    box = gui.Dlg()
    box_key.append('subjnum')
    box.addField("Subject ID:", subjnum)
    box_key.append('imgset')
    box.addField("Image Set", imgset,
                 choices=['A', 'B', 'C', 'behave', 'practice'])
    box_key.append('subjdateid')
    box.addField("Date ID:", subjdateid)
    box_key.append('start_runnum')
    box.addField("Run number:", 1)
    box_key.append('show_instructions')
    box.addField("instructions?", show_instructions)
    box_key.append('isfullscreen')
    box.addField("fullscreen?", isfullscreen)
    box_key.append('ET_type')
    box.addField("eyetracking", ET_opts.get(default_type),
                 choices=['arrington', 'pylink', 'TTL', None])
    box_key.append('usePP')
    box.addField("TTL Trigger?", usePP_opt.get(default_type))
    box_key.append('tasktype')
    box.addField("timing type", default_type, choices=run_total_time.keys())
    box_key.append('timepoint')
    box.addField("Time Point", timepoint, choices=[0, 1, 2, 3, 4])
    box_key.append('nruns')
    box.addField("total # runs", nruns)
    box_key.append('usePD')
    box.addField("PhotoDiode?", calEyeScreen)
    box_key.append('vertOffset')
    box.addField("Vert offset (fraction of screen)", vertOffset)
    box_key.append('midwayPause')
    box.addField("Midway Pause", midwayPause)
    box_key.append('recVideo')
    box.addField("Record Eye Video", recVideo)
    box_key.append('calEyeScreen')
    box.addField("Calibrate Eye", calEyeScreen)

    boxdata = box.show()
    if box.OK:
        subjnum = boxdata[box_key.index('subjnum')]
        imgset = boxdata[box_key.index('imgset')]
        subjdateid = boxdata[box_key.index('subjdateid')]
        start_runnum = int(boxdata[box_key.index('start_runnum')])
        show_instructions = boxdata[box_key.index('show_instructions')]
        isfullscreen = boxdata[box_key.index('isfullscreen')]
        ET_type = boxdata[box_key.index('ET_type')]
        usePP = boxdata[box_key.index('usePP')]
        tasktype = boxdata[box_key.index('tasktype')]
        timepoint = boxdata[box_key.index('timepoint')]
        nruns = int(boxdata[box_key.index('nruns')])
        vertOffset = float(boxdata[box_key.index('vertOffset')])
        midwayPause = boxdata[box_key.index('midwayPause')]
        recVideo = boxdata[box_key.index('recVideo')]
        calEyeScreen = boxdata[box_key.index('calEyeScreen')]
        usePD = boxdata[box_key.index('usePD')]
    else:
        sys.exit(1)


subjid = subjnum + '_' + subjdateid
# maybe we want to auto add date?
# + datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")


# # trials using trialHandler and list of dicts
# possiblepos=[-1, 1, -.75, .75, -.5, .5]
# # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
# (sacc_images,novel_images) = image_sets()

# # put together for saccade trials
# C:\Users\Public\Desktop\Tasks\mgs_encode_memory.py\

# # paths
# like: "subj_info/10931/01_eeg_A"
(datadir, logdir) = getSubjectDataPath(subjid, tasktype,
                                       'mgsenc-' + imgset,
                                       timepoint)

# # get all_runs_info
# all_run_info = {'imagedf': imagedf, 'run_timing': run_timing }
all_runs_info = gen_run_info(nruns, datadir, imgset, task=tasktype)

# TODO:
# if tasktype == 'practice':
#    all_runs_info['imagedf'][1,'imgfile'] = 'img/example.png'
#    all_runs_info['imagedf'][4,'imgfile'] = 'img/example.png'

# 20180717 - redudant but easy easy to set port
#            prev only needed for eeg
# other tasks dont matter if pp address is set
if(tasktype in ['practice', 'behave'] and usePP):
    pp_address = 0x0378
    zeroTTL = False
    print("using practice computer address and zeroing")
else:
    zeroTTL = True
    # pp_address = 0xDFF8
    pp_address = host_type.pp_address

# # screen setup
win = create_window(isfullscreen)
task = mgsTask(win, ET_type=ET_type, usePP=usePP, vertOffset=vertOffset,
               pp_address=pp_address, zeroTTL=zeroTTL,
               recVideo=recVideo, usePD=usePD)


# # instructions
# OR hack to have somthing in image
#    incase we start with a 'None' null image trial
#    (instructions would do this)
if show_instructions:
    task.sacc_instructions()
else:
    pass
    # not needed, we softcode the defsize (225,225)
    # replace_img(task.img, 'img/example.png', 1, task.imgratsize)
    # win.clearBuffer()

# take screenshots:
# takeshots="20171101"
# takeshots = "20180221"
# takeshots = "20180326"
takeshots = None

# this is kludgy. duration is included in timing files
# maybe iti should be an included 1D
if tasktype == 'test':
    mgsdur = .25

for runi in range(start_runnum-1, nruns):
    run = runi + 1
    print("### run %d" % run)

    trialdf = all_runs_info['run_timing'][runi]
    run_getReadyMsg = ("Run %d" % run) + "\n" + getReadyMsg

    seconds = datetime.datetime.strftime(datetime.datetime.now(), "%H%M%S")

    # # logging
    logfilename = "info_%s_%d_%s.log" % (subjid, run, seconds)
    logfile = os.path.join(logdir, logfilename)
    lastLog = logging.LogFile(logfile, level=logging.INFO, filemode='w')
    logging.log(level=logging.INFO,
                msg='run %s, loading at epoch %s' % (run, seconds))
    logging.flush()  # when its okay to write

    # trial settings and timing
    task_info = {'subjid': subjid, 'epoch': seconds}
    if sys.version_info[0] < 3:
        tlist = trialdf.T.to_dict().values() # if py3, remove .values
    else:
        tlist = trialdf.T.to_dict()
    # pyglet label errors? need pip install pglyet==1.3  today
    sacc_trials = data.TrialHandler2(
                    trialList = tlist,
                    nReps=1,
                    method='sequential', extraInfo=task_info)

    # ## Run calibration if we need it
    if calEyeScreen:
        c = showCal(task.win)
        c.calibrate()
    # # run saccade trials
    # blockstarttime=core.getTime()
    eyetrackingfile = '%s_run%d_%s.txt' % (subjid, run, seconds)
    task.eyetracking_newfile('%s' % eyetrackingfile)
    blockstarttime = task.wait_for_scanner(scannerTriggerKeys, run_getReadyMsg)
    logging.log(level=logging.INFO,
                msg='scanner trigger recieved at %d' % blockstarttime)

    # for all trials in this run
    for t in sacc_trials:
        if midwayPause and t['trial'] == int(sacc_trials.nTotal/2.0):
            # setup pause screen
            task.textbox.pos = (-.2, -.1)
            task.textbox.text = 'Half way break!'
            task.iti_fix.draw()
            task.textbox.draw()
            # wait out the previous iti
            break_at = blockstarttime + t['cue']
            wait_until(break_at)
            # and pause
            task.send_code('end', None, None)

            # wait for a keep press then flip
            task.instruction_flip()

            # dispaly another screen before going into task
            task.textbox.pos = (-.2, 0)
            task.textbox.text = 'Ready!?'
            task.textbox.draw()
            task.instruction_flip()

            # compensate for break in future onsets
            task.addTime = core.getTime() - break_at
            task.send_code('start', None, None)

        # run the trial
        fliptimes = task.sacc_trial(t, blockstarttime + task.addTime,
                                    takeshots=takeshots, logh=logging)

        # give mgs it's time then put up the iti cross
        mgsoff = blockstarttime + t['mgs'] + mgsdur + task.addTime
        wait_until(mgsoff)
        fliptimes['iti'] = task.run_iti()

        # and take a screenshot if we want it
        if takeshots:
            take_screenshot(win, takeshots + '_05_iti')
            break

        # add fliptimes
        for k, v in fliptimes.items():
            sacc_trials.addData(k + '_flip', v)

    # finish up
    task.run_iti()
    # undo any extra waiting
    task.addTime = 0

    savefile_csv = '%s_%s_%d_view.csv' % (subjid, tasktype, run)
    savefile_csv_path = os.path.join(datadir, savefile_csv)
    print('saving %s' % savefile_csv_path)
    sacc_trials.data.to_csv(savefile_csv_path)

    thisendtime = run_total_time[tasktype] + blockstarttime
    print("running to end of time (%.02f, actual %.02f)" %
          (run_total_time[tasktype], thisendtime))
    wait_until(thisendtime)
    logging.flush()
    # end ttl/close eyefile, show finsihed text
    # option for quiting early
    end_info = task.run_end(run, nruns)
    print(end_info)
    print(end_info == "done")
    if end_info == "done":
        break

# done will all runs
win.close()
