#!/usr/bin/env python
# -*- elpy-use-ipython: "ipython"; -*-

from psychopy import gui
import psychopy
import numpy as np
import pandas as pd
import sys
import os
import datetime
from mgs_task import mgsTask, wait_until,\
                     shuf_for_ntrials, replace_img, getSubjectDataPath
from host_info import host_tasktype

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def gobal_quit_key(key='escape'):
    if not psychopy.event.globalKeys.get(key):
        psychopy.event.globalKeys.add(key=key, func=psychopy.core.quit, name='shutdown')

#
# vgs or anti (color of cross, value of trigger code)
#


# ---------- TASK CONFIG ----------------------
# how long to wait at each event
# iti is only variable, num trials set on lenght of iti vec
dur = {'iti': [1]*20 + [1.5]*10 + [2]*5 + [2.5]*3 + [3]*2,
       'cue': .5,
       'dot': 1
       }
positions = [-1, -.5, .5, 1]

cue_colors = {'anti': 'red', 'vgs': 'green'}
cue_instrs = {'anti': 'away from', 'vgs': 'to'}

host = host_tasktype()

# ---------- RUN SETTINGS --------------------
datestr = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
# get settings with gui prompt
settings = {'subjid': '',
            'dateid': datestr,
            'tasktype': ['vgs', 'anti'],
            'timepoint': datetime.datetime.now().year - 2017,
            'fullscreen': True,
            'instructions': True,
            'usePP': True,
            'ET_type': [host.ET, None, 'arrington', 'pylink']}
box = gui.DlgFromDict(settings,
                      order=['subjid', 'dateid', 'tasktype', 'timepoint',
                             'fullscreen', 'instructions', 'usePP', 'ET_type'])
if not box.OK:
    sys.exit(1)

# # paths
# like: "subj_info/10931/01_eeg_anti"
subjid = settings['subjid'] + '_' + settings['dateid']
(datadir, logdir) = getSubjectDataPath(subjid,
                                       'eeg',
                                       settings['tasktype'],
                                       settings['timepoint'])

cue_color = cue_colors[settings['tasktype']]
cue_instr = cue_instrs[settings['tasktype']]


# ---- TTL
# VGS
#  cue:  1  2  4  5
#  dot: 51 52 54 55
# ANTI
#  cue: 101 103 104 105
#  dot: 151 153 154 155
eventTTLlookup = {'cue': 0, 'dot': 50}  # iti = 254 | start = 128 | end = 129


def print_and_ttl(event, pos, tasktype=settings['tasktype']):
    # left to right 1 to 5 from -1 -.5 .5 1 | no 0 (center), never see 3
    pos_code = pos*2 + 3
    ttl = pos_code + \
        eventTTLlookup.get(event, 0) +\
        100 * int(tasktype == 'anti')
    # send code
    print('%s at %d: ttl %d' % (event, pos, ttl))
    if settings['usePP']:
        task.send_ttl(ttl)
    if settings['ET_type'] is not None:
        print(settings['ET_type'])
        task.set_et_event("%d=%s@%d" % (ttl, event, pos))


# ---------- TIMING --------------------

# length of itis sets the number of trials
ntrials = len(dur['iti'])
itis = [dur['iti'][i] for i in np.random.permutation(ntrials)]
pos = shuf_for_ntrials(positions, ntrials)

# ---------- GO --------------------------
# setup task (get send_ttl, crcl, iti_fix)
task = mgsTask(None,
               usePP=settings['usePP'],
               ET_type=settings['ET_type'],
               fullscreen=settings['fullscreen'],
               pp_address=host.pp_address)

# escape to exit
gobal_quit_key()

# tell the eye tracker we want a new file
sub_ses = settings['subjid'] + '_' + str(settings['timepoint']) + "_" + settings['dateid'] + settings['tasktype']
task.eyetracking_newfile(sub_ses)
if settings['ET_type'] == 'pylink':
    # eyelink only gets 8 characters, and will be something like the date
    # so we'll send a message to the file so we have some way of looking at it
    task.eyelink.el.sendMessage("NAME: %s"%sub_ses)

# instructions
if settings['instructions']:
    task.textbox.pos = (-.9, 0)
    task.textbox.text = \
        'STEPS:\n\n' + \
        '1. relax, look at center white cross\n\n' +\
        '2. get ready when you see the %s cross\n\n' % cue_color + \
        '3. look %s the dot when it appears\n\n' % cue_instr

    task.textbox.draw()
    task.instruction_flip()

# start task, also sends start ttl code
starttime = task.wait_for_scanner(['space'], 'Ready?')

# could do inside loop, but never changes
task.cue_fix.color = cue_color

nextonset = starttime
timing = []
for ri in range(ntrials):
    # this run settings
    this_pos = pos[ri]
    flip = {'start': nextonset, 'pos': this_pos, 'itidur': itis[ri]}

    nextonset += itis[ri]

    # show cue colored fix
    cueon = nextonset
    task.cue_fix.draw()
    task.win.callOnFlip(print_and_ttl, 'cue', this_pos)
    wait_until(cueon)
    flip['cue'] = task.win.flip()
    nextonset += dur['cue']

    # show dot
    doton = nextonset
    imgpos = replace_img(task.img, None, this_pos, task.imgratsize)
    task.crcl.pos = imgpos
    task.crcl.draw()
    task.win.callOnFlip(print_and_ttl, 'dot', this_pos)
    wait_until(doton)
    flip['dot'] = task.win.flip()
    nextonset += dur['dot']

    # show iti colored fixation cross
    ition = nextonset
    task.iti_fix.draw()
    task.win.callOnFlip(task.log_and_code, 'iti', None, None)
    wait_until(ition)
    flip['iti'] = task.win.flip()

    # log flip times
    print(flip)
    timing.append(flip)

# ---------- WRAP UP --------------------------
# wait an iti length
wait_until(nextonset + .5)
# save
seconds = datetime.datetime.strftime(datetime.datetime.now(), "%Y%M%d%H%M%S")
saveas = os.path.join(datadir, 'runinfo_%s.csv' % seconds)
if settings['ET_type'] == 'pylink':
    saveas_edf = os.path.join(datadir, '%s.edf' % seconds)
    task.eyelink.el.closeDataFile()
    task.eyelink.el.receiveDataFile("",saveas_edf)

print('saving to %s' % saveas)
pd.DataFrame(timing).to_csv(saveas)
# end task: send code and put up end screen
if settings['usePP']:
    task.send_ttl(129)
#task.wait_for_scanner(['space'], 'Finished!')
task.run_end()
task.win.close()
