#!/usr/bin/env python
# -*- elpy-use-ipython: "ipython"; -*-

from mgs_task import mgsTask, wait_until
import numpy as np

isfullscreen = False
# if we are fullscreen, we're at eeg and want to send ttl too
useArrington = isfullscreen

# how long to wait at each event
fixdur = .5
dotdur = .5

# setup task (get send_ttl, crcl, iti_fix)
task = mgsTask(None, fullscreen=isfullscreen, useArrington=useArrington)

# get 20 positions from 10% to 90%
pos = np.linspace(.1, .9, 20)
allpos = np.concatenate([pos, -1 * pos])
ridx = np.random.permutation(len(allpos))


def print_and_ttl(msg, pos):
    print(msg)
    event = "look"
    side = "Left"
    if pos > .5:
        side = "Right"
    if pos == .5:
        event = "fix"
        side = "center"
    if useArrington:
        task.send_code(event, side, pos)


# -- instructions
task.textbox.pos = (-.9, 0)
task.textbox.text = \
       'Callibration\n\n' + \
       '1. look at center cross\n\n' +\
       '2. look at the dot\n\n' + \
       '3. return to cross'
task.textbox.draw()
task.instruction_flip()

# -- start
task.wait_for_scanner(['space'], 'Ready?')
# wait for scan sends start code
task.send_code('start', None, None)

winwidth = task.win.size[0]/2
print(winwidth)
for ri in range(len(ridx)):
    # find position and ttlcode
    i = ridx[ri]
    p = allpos[i] * winwidth

    fixttl = .5
    posttl = allpos[i]

    # draw cricle
    task.crcl.pos = (p, 0)
    task.crcl.draw()
    task.win.callOnFlip(print_and_ttl,
                        "p at %.02fx (%.02fpx)" % (allpos[i], p),
                        posttl)
    ft = task.win.flip()
    # wait a bit
    wait_until(ft + dotdur)

    # for testing
    # event.waitKeys()

    # draw cross
    task.iti_fix.draw()
    task.win.callOnFlip(print_and_ttl, "back to fix", fixttl)
    ft = task.win.flip()
    # wait a bit
    wait_until(ft + fixdur)


# all done, wrap up
task.send_code('end', None, None)
task.run_end()
task.win.close()
