#!/usr/bin/env python3
# https://www.psychopy.org/api/iohub/device/eyetracker_interface/SR_Research_Implementation_Notes.html
from psychopy.iohub import launchHubServer
from psychopy.core import getTime, wait


iohub_config = {'eyetracker.hw.sr_research.eyelink.EyeTracker':
                {'name': 'tracker',
                 'model_name': 'EYELINK 1000 DESKTOP',
                 'runtime_settings': {'sampling_rate': 500,
                                      'track_eyes': 'RIGHT'}
                 }
                }
io = launchHubServer(**iohub_config)

# Get the eye tracker device.
tracker = io.devices.tracker

# run eyetracker calibration
# either host or display:
#  C = start cal, V = start val
#  ENTER = accept, ESC = return to blank screen
#  O = exit adn continue
r = tracker.runSetupProcedure()


# tracker.sendCommand()
tracker.setRecordingState(True)
tracker.sendMessage("hi")

# opening file and start/stop recording maybe needs
#tracker.sendCommand(key,value=None)
