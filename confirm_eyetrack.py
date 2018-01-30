#!/usr/bin/env python
from psychopy import visual, core,  event, logging
from mgs_task import mgsTask, msg_screen
import datetime

# todo test if eyetracking streamer is open
# [ psutil.Process(p).name() for p in psutil.pids() ]

win = visual.Window([400, 300])
textbox = visual.TextStim(win, text='**',name='generic_textbox',alignHoriz='left',color='white',wrapWidth=2)

msg_screen(win,textbox,'load eyetracker? (push any key)')
task = mgsTask(win, useArrington=True)

msg_screen(win,textbox,'open file? (push anykey)')

seconds = datetime.datetime.strftime(datetime.datetime.now(), "%H%M%S")
task.eyetracking_newfile('test_eyetracking_%s' % seconds)

msg_screen(win,textbox,'start tracking? (push anykey)')
task.start_aux()

msg_screen(win,textbox,'send "TTL"? (push anykey)')
task.vpx.VPX_SendCommand('dataFile_InsertString "test"')

msg_screen(win,textbox,'send 2nd "TTL"? (push anykey)')
task.vpx.VPX_SendCommand('dataFile_InsertString "second"')

msg_screen(win,textbox,'close eye file (push anykey)')
task.stop_aux()
msg_screen(win,textbox,'(any key to quit)')
