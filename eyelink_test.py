#!/usr/bin/env python3
from pylink_help import eyelink
print("eyelink via pylink")
el = eyelink([800 600])
el.trigger("trigger0")
el.open("testing")
el.start()
el.trigger("trigger1")
el.eyeTrkCalib()
el.trigger("trigger2")
el.stop()
