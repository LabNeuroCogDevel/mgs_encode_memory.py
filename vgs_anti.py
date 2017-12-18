#!/usr/bin/env python
# -*- elpy-use-ipython: "ipython"; -*-

from psychopy import visual, core, data, event, gui
from mgs_task import mgsTask, wait_until, shuf_for_ntrials, replace_img
import numpy as np
import pandas as pd
import sys

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


# ---------- RUN SETTINGS --------------------
# get settings with gui prompt
settings = {'tasktype': ['vgs', 'anti'], 'fullscreen': True,
            'instructions': True, 'usePP': True}
box = gui.DlgFromDict(settings)
if not box.OK:
    sys.exit(1)

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
          eventTTLlookup.get(event,0) +\
          100 * int(tasktype == 'anti')
    # send code
    print('%s at %d: ttl %d' % (event,pos,ttl) )
    if settings['usePP']:
        task.send_ttl(ttl)


# ---------- TIMING --------------------

# length of itis sets the number of trials
ntrials = len(dur['iti'])
itis = [dur['iti'][i] for i in np.random.permutation(ntrials)]
pos = shuf_for_ntrials(positions,ntrials)

    
# ---------- GO --------------------------
# setup task (get send_ttl, crcl, iti_fix)
task = mgsTask(None, usePP=settings['usePP'], fullscreen=settings['fullscreen'])

# instructions
if settings['instructions']:
    task.textbox.pos = (-.9, 0)
    task.textbox.text = \
           'STEPS:\n\n'+ \
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
timing=[]
for ri in range(ntrials):
    # this run settings
    this_pos=pos[ri]
    flip = {'start': nextonset, 'pos': this_pos, 'itidur': itis[ri] }

    nextonset += itis[ri]

    # show cue colored fix
    cueon = nextonset 
    task.cue_fix.draw()
    task.win.callOnFlip(print_and_ttl,'cue',this_pos)
    wait_until(cueon)
    flip['cue'] = task.win.flip()
    nextonset += dur['cue']

    # show dot
    doton = nextonset
    imgpos = replace_img(task.img, None, this_pos, task.imgratsize)
    task.crcl.pos = imgpos
    task.crcl.draw()
    task.win.callOnFlip(print_and_ttl, 'dot',this_pos)
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
# all done, wrap up
wait_until(nextonset + .5)
task.send_ttl(129)  # end task
task.wait_for_scanner(['space'], 'Finished!')
task.win.close()
