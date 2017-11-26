#!/usr/bin/env python2
# -*- py-which-shell: "python2"; -*-

# https://github.com/psychopy/psychopy/blob/master/psychopy/demos/coder/experiment%20control/TrialHandler.py
# on archlinux, python is python3
# ^M-: (run-python "/usr/bin/python2")

from __future__ import division
from psychopy import visual, core, data, logging, gui, event
import datetime
import glob, re, math, numpy,sys,os
# del sys.modules['mgs_task'];
from mgs_task import *
#subjnum='0'; win = visual.Window([800,600]); task = mgsTask(win)

os.chdir( os.path.dirname(os.path.realpath(__file__) ) )


## get subj info
if (len(sys.argv)>1):
    subjnum=sys.argv[1]
else:
    box = gui.Dlg()
    box.addField("Subject ID:")
    box.show()
    subjnum=box.data[0]

subjid=subjnum + datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")
seconds=datetime.datetime.strftime(datetime.datetime.now(),"%H%M%S")


## logging
if not os.path.exists('log'):
    os.mkdir('log')
logfile=os.path.join('log',"info_%s_%s.log"%(subjid,seconds))
lastLog = logging.LogFile(logfile, level=logging.INFO, filemode='w')
logging.log(level=logging.INFO, msg='starting at %s'%core.Clock())
logging.flush() # when its okay to write
# timing
blocktimer = core.Clock()


## settings
# trials using trialHandler and list of dicts
#possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
#(sacc_images,novel_images) = image_sets()

## put together for saccade trials
# C:\Users\Public\Desktop\Tasks\mgs_encode_memory.py\
#sacc_stimList= gen_stimlist(sacc_images,possiblepos,os.path.join('stims','example_00001_'))

# TODO:
# - read from file if we already generated
# - write to file if we dont already have
# - use different timing for each run
path_dict={'Indoor': ['SUN/circle_select/inside/*png'],
           'Outdoor': ['SUN/circle_select/outside_man/*png',
                       'SUN/circle_select/outside_nat/*png',
                      ]
          }
imagedf = gen_imagedf(path_dict) 
# TODO: repeat for all runs
for run in [1]:
    timingglob=os.path.join('stims','8344728414871514311','*')
    trialdf = parse_onsets(timingglob)
    (imagedf, trialdf) = gen_stimlist_df(imagedf,trialdf)

# quick check
#if( any(numpy.diff([x['vgs'] for x in trialdf ]) < 0 ) ):
if( any(numpy.diff(trialdf.vgs) < 0 ) ):
    raise Exception('times are not monotonicly increasing! bad timing!')
# TODO: get df of this run
print(trialdf.head()) # TODO: remove print

sacc_trials = data.TrialHandler2(trialdf.T.to_dict().values(),1,method='sequential',extraInfo ={'subjid': subjid, 'epoch': seconds})

#accept_keys = {'known':'k', 'unknown': 'd', 'left':'d','right':'k', 'oops':'o' }
accept_keys = {'known':'2', 'unknown': '3', 'left':'2','right':'3', 'oops':'1' }



## screen setup
#win = visual.Window([400,400],screen=0)
#win = visual.Window(fullscr=True)
win = visual.Window([800,600])
win.winHandle.activate() # make sure the display window has focus
win.mouseVisible=False # and that we dont see the mouse

task = mgsTask(win,accept_keys)

## instructions
task.sacc_instructions()

# take screenshots:
takeshots=None
#takeshots="20171101"

## run saccade trials
#blockstarttime=core.getTime()
blockstarttime=task.wait_for_scanner(['asciicircum','equal','escape','6']) # ^, =, or esc
for t in sacc_trials:
    task.sacc_trial(t,blockstarttime,takeshots=takeshots)
    # this is unnecessary
    sacc_trials.addData('startTime',t['cue'] + blockstarttime)
    sacc_trials.addData('imgon',t['vgs'] + blockstarttime)
    sacc_trials.addData('dlyon',t['dly'] + blockstarttime)
    sacc_trials.addData('mgson',t['mgs'] + blockstarttime)
    sacc_trials.addData('delaylen', t['mgs'] - t['dly'])
    task.run_iti() #.5)
    if takeshots:
        take_screenshot(win,takeshots+'_05_iti')
        break

#sacc_trials.saveAsText(subjid + '_view.txt')
sacc_trials.data.to_csv(subjid + '_view.csv')


print("running 12 second iti")
task.run_iti(12)

## run recall quiz trials
#blocktimer.reset()

# this should work but does not!
#recall_trails.data.to_csv(subjid + '_recall.csv')

logging.flush()
# TODO save recall_trials and sacc_trials
win.close()

