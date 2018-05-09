#!/usr/bin/env python
# -*- elpy-use-ipython: "ipython"; -*-

from mgs_task import mgsTask, wait_until
import numpy as np
from psychopy import gui  # , event
import datetime
import sys

tracking_type = "pupil"
box = gui.Dlg()
box.addField("traking type/file name:", tracking_type)
boxdata = box.show()
if box.OK:
    tracking_type = boxdata[0]
else:
    sys.exit(1)



isfullscreen = True
# if we are fullscreen, we're at eeg and want to send ttl too
useArrington = isfullscreen

# how long to wait at each event
fixdur = .75
dotdur = .75


# setup task (get send_ttl, crcl, iti_fix)
task = mgsTask(None, fullscreen=isfullscreen, useArrington=useArrington)

# start eyetracking file
seconds = datetime.datetime.strftime(datetime.datetime.now(), "%H%M%S")
eyetrackingfile = '%s_run_%s.txt' % (tracking_type, seconds)
task.eyetracking_newfile('%s' % eyetrackingfile)


# get 20 positions from 10% to 90%
pos = np.linspace(.1, .9, 20)

# concat + and - versions
allpos = np.concatenate([pos, -1 * pos])
# randomly position them
ridx = np.random.permutation(len(allpos))
allpos = allpos[ridx]
# repeat each position in order e.g. [ .9,.9, -.1,-.1, ...]
pos_rep = np.array([[x,x] for x in allpos ]).reshape(1,len(allpos)*2)[0]
# ridx is 0:n, randomness happened earlier
ridx = range(pos_rep.size)

# trigger to use
def print_and_ttl(msg, pos):
    print(msg)
    event = "look"
    side = "Left"
    if pos > 0:
        side = "Right"
    if pos == 0:
        event = "fix"
        side = "center"
    if useArrington:
        task.send_code(event, side, pos)
    else:
        print("%s %s %.02f" % (event, side,pos))


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
task.start_aux()
#task.vpx.VPX_SendCommand('dataFile_Pause 0')
for ri in range(len(ridx)):
    # find position and ttlcode
    i = ridx[ri]
    p = pos_rep[i] * winwidth

    fixttl = 0
    posttl = pos_rep[i]

    # draw cricle
    task.crcl.pos = (p, 0)
    task.crcl.draw()
    task.win.callOnFlip(print_and_ttl,
                        "p at %.02fx (%.02fpx)" % (pos_rep[i], p),
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
task.stop_aux()
task.run_end()
task.win.close()
task.stop_aux()
