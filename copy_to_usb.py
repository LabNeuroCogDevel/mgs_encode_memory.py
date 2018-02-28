#!/usr/bin/env python

from subprocess import call
import os

absfile=os.path.abspath(__file__)
print(absfile)
os.chdir(os.path.dirname(absfile))

# copy local task data
call(["robocopy", "subj_info",  "E:\\subj_info",  "/e", "/XO" ]) # "/L" for list only
# and maybe eyetracking too?
#call(["robocopy", "?:\\ET  E:\\subj_info\\eye_data  /XO /l "])

raw_input("\nFINISHED\npush enter to end")
