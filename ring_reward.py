#!/usr/bin/env python3
# -*- elpy-use-ipython: "ipython"; -*-

from psychopy import gui, misc, visual
from mgs_task import mgsTask, wait_until,\
                     shuf_for_ntrials, replace_img, getSubjectDataPath
import numpy as np
import pandas as pd
import sys
import os
import datetime

os.chdir(os.path.dirname(os.path.realpath(__file__)))

#
# vgs or anti (color of cross, value of trigger code)
#


# ---------- TASK CONFIG ----------------------
# how long to wait at each event
# iti is only variable, num trials set on lenght of iti vec
dur = {'iti': 1, 'rew': 1, 'cue': 1, 'dot': 1}

# positions are -1 far left to 1 far right
positions = [-1, -.5, .5, 1]

# reward tyes have different colors and symbols
cues = {'neu': {'color': 'gray', 'sym': '#'},
        'rew': {'color': 'green', 'sym': '$'}}

# what color is the + in the center of the screen during cue
# red usualy used for anti saccade tasks
cue_fix_color = 'red'


# ---------- RUN SETTINGS --------------------
datestr = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
# get settings with gui prompt
settings = {'_subjid': '',
            'ntrials': 28,
            'dateid': datestr,
            'timepoint': datetime.datetime.now().year - 2019,
            'fullscreen': True,
            'instructions': True,
            'usePP': True}

box = gui.DlgFromDict(settings)
if not box.OK:
    sys.exit(1)

# # paths
# like: "subj_info/10931/01_eeg_anti"
subjid = settings['_subjid'] + '_' + settings['dateid']
(datadir, logdir) = getSubjectDataPath(subjid, 'behave', 'ringreward',
                                       settings['timepoint'])

# ---- TTL
# neu
#  rew:  1  2  4  5
#  cue: 21 22 24 25
#  dot: 51 52 54 55
# rew
#  rew: 101 102 104 105
#  cue: 121 122 124 125
#  dot: 151 152 154 155

# side is added to these base trigger values
eventTTLlookup = {'rew': 0, 'cue': 20, 'dot': 50}
# iti = 254 | start = 128 | end = 129


def print_and_ttl(event, pos, trialtype):
    """ determin what ttl trigger should be based on
        event, position, and trialtype
        eventTTLlookup is global var dictionary with TTL offset
    """
    # left to right 1 to 5 from -1 -.5 .5 1 | no 0 (center), never see 3
    pos_code = pos*2 + 3
    ttl = pos_code + \
        eventTTLlookup.get(event, 0) +\
        100 * int(trialtype == 'rew')
    # send code
    print('%s at %d: ttl %d' % (event, pos, ttl))
    if settings['usePP']:
        task.send_ttl(ttl)


# ---------- TIMING --------------------

# length of itis sets the number of trials
ntrials = settings['ntrials']
pos = shuf_for_ntrials(positions, ntrials)
rewtype = shuf_for_ntrials(['rew', 'neu'], ntrials)

# ---------- GO --------------------------
# setup task (get send_ttl, crcl, iti_fix)
task = mgsTask(None,
               usePP=settings['usePP'],
               fullscreen=settings['fullscreen'])

# ----- DRAW A RING OF $ OR  --------

# create the ring, see
# https://discourse.psychopy.org/t/the-best-way-to-draw-many-text-objects-rsvp/2758
n_in_ring = 12
el_rs = 250  # TODO: make relative to screen size?
el_thetas = np.linspace(0, 360, n_in_ring, endpoint=False)
el_xys = np.array(misc.pol2cart(el_thetas, el_rs)).T
text_size = 45
ringtext = visual.TextStim(win=task.win, units='pix', bold=True,
                           height=text_size, text='$')  # '$' will be changed
cap_rect_norm = [
    -(text_size / 2.0) / (task.win.size[0] / 2.0),  # left
    +(text_size / 2.0) / (task.win.size[1] / 2.0),  # top
    +(text_size / 2.0) / (task.win.size[0] / 2.0),  # right
    -(text_size / 2.0) / (task.win.size[1] / 2.0)   # bottom
]
ringimg = {}
for k in ['rew', 'neu']:
    ringtext.text = cues[k]['sym']
    ringtext.color = cues[k]['color']
    buff = visual.BufferImageStim(
        win=task.win,
        stim=[ringtext],
        rect=cap_rect_norm
    )
    # img = (np.flipud(np.array(buff.image)[..., 0]) / 255.0 * 2.0 - 1.0)
    ringimg[k] = visual.ElementArrayStim(
        win=task.win,
        units="pix",
        nElements=n_in_ring,
        sizes=buff.image.size,
        xys=el_xys,
        # colors=cues[k]['color'],
        elementMask=None,
        elementTex=buff.image)

# -----  INSTRUCTIONS ------
if settings['instructions']:
    cuesym = cues['rew']['sym']
    task.textbox.pos = (-.9, 0)
    task.textbox.text = \
        'STEPS:\n\n' + \
        '1. Relax. Look at the center white cross\n\n' +\
        '2. If you see a %s ring, you can get points\n\n' % cuesym +\
        '3. Get ready when you see the %s cross\n\n' % cue_fix_color +\
        '4. Look opposite the dot when it appears\n\n'

    task.textbox.draw()
    task.instruction_flip()

# -----  ACTUALLY RUN TASK ------

# start task, also sends start ttl code
starttime = task.wait_for_scanner(['space'], 'Ready?')

# could do inside loop, but never changes

nextonset = starttime
timing = []
for ri in range(ntrials):
    # this run settings
    this_pos = pos[ri]
    this_rew = rewtype[ri]
    flip = {'start': nextonset, 'pos': this_pos, 'rew': this_rew}

    nextonset += dur['iti']

    # reward display setup
    rewon = nextonset
    ringimg[this_rew].draw()
    task.cue_fix.color = 'white'
    task.cue_fix.draw()
    task.win.callOnFlip(print_and_ttl, 'rew', this_pos, this_rew)
    # timing
    wait_until(rewon)
    flip['rew'] = task.win.flip()
    nextonset += dur['rew']

    # cue setup
    cueon = nextonset
    task.cue_fix.color = cue_fix_color
    task.win.callOnFlip(print_and_ttl, 'cue', this_pos, this_rew)
    task.cue_fix.draw()
    # timing
    wait_until(cueon)
    flip['cue'] = task.win.flip()
    nextonset += dur['cue']

    # show dot
    doton = nextonset
    imgpos = replace_img(task.img, None, this_pos, task.imgratsize)
    task.crcl.pos = imgpos
    task.crcl.draw()
    task.win.callOnFlip(print_and_ttl, 'dot', this_pos, this_rew)
    # timing
    wait_until(doton)
    flip['dot'] = task.win.flip()
    nextonset += dur['dot']

    # show iti colored fixation cross
    ition = nextonset
    task.iti_fix.draw()
    task.win.callOnFlip(task.log_and_code, 'iti', None, None)
    # timing
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
print('saving to %s' % saveas)
pd.DataFrame(timing).to_csv(saveas)
# end task: send code and put up end screen
if settings['usePP']:
    task.send_ttl(129)

# task.wait_for_scanner(['space'], 'Finished!')
task.run_end()
task.win.close()
