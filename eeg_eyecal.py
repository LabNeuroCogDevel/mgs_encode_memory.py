#!/usr/bin/env python
# -*- elpy-use-ipython: "ipython"; -*-

from psychopy import visual, core, data
from mgs_task import mgsTask, replace_img
import random

isfullscreen = False


if isfullscreen:
    win = visual.Window(fullscr=True)
else:
    win = visual.Window([800, 600])

win.winHandle.activate()  # make sure the display window has focus
win.mouseVisible = False  # and that we don't see the mouse

task = mgsTask(win, usePP = False)

sides=['Left','NearLeft','NearRight','Right']
nreps_each=10

reps=[s for s in sides for  i in range(nreps_each)]
random.shuffle(reps)

for side in reps:
    task.vgs_show(0,side)
    core.wait(.5)
    task.run_iti()
    core.wait(.2)

win.close()
