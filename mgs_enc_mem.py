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
    start_runnum=1
    show_instructions=True
else:
    box = gui.Dlg()
    box.addField("Subject ID:")
    box.addField("Run number:",1)
    box.addField("instructions?",True)
    boxdata = box.show()
    if box.OK:
        subjnum=boxdata[0]
        start_runnum=int(boxdata[1])
        show_instructions=boxdata[2]
    else:
        sys.exit(1)

subjid=subjnum #+ datetime.datetime.strftime(datetime.datetime.now(),"_%Y%m%d")
seconds=datetime.datetime.strftime(datetime.datetime.now(),"%H%M%S")




## settings
run_total_time = 420
# TODO check against traildf max
nruns = 4

# trials using trialHandler and list of dicts
#possiblepos=[-1, 1, -.75, .75, -.5, .5] # numpy.linspace(.5,1,3).reshape(-1,1) * (-1,1)
#(sacc_images,novel_images) = image_sets()

## put together for saccade trials
# C:\Users\Public\Desktop\Tasks\mgs_encode_memory.py\
#sacc_stimList= gen_stimlist(sacc_images,possiblepos,os.path.join('stims','example_00001_'))


# # paths
savepath = 'subj_info'
datadir = os.path.join(savepath,subjid)
logdir = os.path.join(datadir,'log')
for thisoutdir in [savepath, datadir, logdir]:
    if not os.path.exists(thisoutdir):
        os.makedirs(thisoutdir)

# # get all_runs_info
# all_run_info = {'imagedf': imagedf, 'run_timing': run_timing }
all_runs_info = gen_run_info(nruns,datadir)

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
if show_instructions:
    task.sacc_instructions()
else:
    # hack to have somthing in image incase we start with a 'None' null image trial
    # instructions would do this 
    replace_img(task.img,'img_circle/winter.02.png',1,task.imgratsize)
    win.flip()
    win.flip()

# take screenshots:
takeshots=None
#takeshots="20171101"

for runi in range(start_runnum-1,nruns):
    run = runi + 1
    print("### run %d" % run)
    trialdf = all_runs_info['run_timing'][runi]
    ## logging
    logfile=os.path.join('log',"info_%s_%s.log"%(subjid,seconds))
    lastLog = logging.LogFile(logfile, level=logging.INFO, filemode='w')
    logging.log(level=logging.INFO, msg='starting at %s'%core.Clock())
    logging.flush() # when its okay to write
    
    # timing
    blocktimer = core.Clock()
    sacc_trials = data.TrialHandler2(trialdf.T.to_dict().values(),1,method='sequential',extraInfo ={'subjid': subjid, 'epoch': seconds})
    
    ## run saccade trials
    #blockstarttime=core.getTime()
    blockstarttime=task.wait_for_scanner(['asciicircum','equal','escape','6']) # ^, =, or esc
    for t in sacc_trials:
        task.sacc_trial(t,blockstarttime,takeshots=takeshots)
        task.run_iti() #.5)
        if takeshots:
            take_screenshot(win,takeshots+'_05_iti')
            break
    
    # finish up
    task.run_iti()

    #sacc_trials.saveAsText(subjid + '_view.txt')
    savefile_csv = '%s_%d_view.csv' % (subjid,run)
    savefile_csv_path = os.path.join(datadir,savefile_csv)
    print('saving %s' % savefile_csv_path )
    sacc_trials.data.to_csv(savefile_csv_path)
    
    thisendtime = run_total_time + blockstarttime
    print("running to end of time (%.02f, actual %.02f)" % (run_total_time, thisendtime))
    wait_until(thisendtime)
    task.run_end(run,nruns)
    logging.flush()

win.close()

