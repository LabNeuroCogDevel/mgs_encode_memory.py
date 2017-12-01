#!/usr/bin/env python
from psychopy import visual, core,  event, logging
from mgs_task import mgsTask, msg_screen

win = visual.Window([400, 300])
textbox = visual.TextStim(win, text='**',name='generic_textbox',alignHoriz='left',color='white',wrapWidth=2)

msg_screen(win,textbox,'load eyetracker? (push any key)')
task = mgsTask(win, useArrington=True)

msg_screen(win,textbox,'open file? (push anykey)')
task.eyetracking_newfile('test_eyetracking')

msg_screen(win,textbox,'start tracking? (push anykey)')
task.eyetracking_start()

msg_screen(win,textbox,'send "TTL"? (push anykey)')
task.send_code('test_string_insert')

msg_screen(win,textbox,'(any key to quit)')