#!/usr/bin/env python
from psychopy import visual, core, logging
from mgs_task import mgsTask, msg_screen
from host_info import host_tasktype


host = host_tasktype()
win = visual.Window([400, 300])
textbox = visual.TextStim(win, text='**', name='generic_textbox',
                          alignHoriz='left', color='white', wrapWidth=2)

msg_screen(win, textbox, 'load parallel port and eyetracker? (push any key)')
task = mgsTask(win, ET_type='pylink', usePP=True, pp_address=host.pp_address)


msg_screen(win, textbox, 'send ttl=100 (push anykye)')
task.send_ttl(100)

msg_screen(win, textbox, 'send ttl=200 (push anykey)')
task.send_ttl(100)


msg_screen(win, textbox, 'open file? (push anykey)')

task.eyetracking_newfile('testf1')

msg_screen(win, textbox, 'start tracking? (push anykey)')
task.start_aux()

msg_screen(win, textbox, 'send eyetracking event (push anykey)')
task.eyelink.trigger("test1")

msg_screen(win, textbox, 'send 2nd eyetracking event (push anykey)')
task.eyelink.trigger("test2")

msg_screen(win, textbox, 'send example task event (push anykey)')
task.send_code('cue', 'Outdoor', 'Left', 10)

msg_screen(win, textbox, 'close eye file (push anykey)')
task.stop_aux()

msg_screen(win, textbox, '(any key to quit)')
