#!/usr/bin/env python2

"""
quick psychopy task to print time difference between successive key pushes
intened to help get a sense of the ep3d BOLD tr (diff between '=' pushes)
"""

import time
import psychopy.visual as v
import psychopy.event as e

save_to = "TR_keydiff_%0.0f.txt" % time.time()
outlog = open(save_to, 'w')

win = v.Window(size=[400,400])
disp = v.TextStim(win, text='Escape to quit\n\nsaving to:\n%s' % save_to, color='black')
prev_time = 0

# startup
disp.draw()
win.flip()

while(True):
    # get time diff between this and prev key push
    pushes = e.waitKeys(timeStamped=True)
    (keypush, keytime) = pushes[0]
    time_diff = keytime - prev_time
    prev_time = keytime

    # show 
    text = "%s %.04f %.04f" % (keypush, keytime, time_diff)
    outlog.write(text)
    print(text)
    disp.text = text
    disp.draw()
    win.flip()

    # escape hatch
    if 'escape' in keypush:
        break
