#!/usr/bin/env python2
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from arrington import read_arrington, add_cal_timing, et_3part_trigger
#
# Usage: 
#   ./cal_score.py cal/20181116_7tgood/M*{run,tim}*
#   give eye(run) file, task(timing) file
#

# need at least a calibration file
# and maybe a event timing file
# eyefile="/home/foranw/src/tasks/mgs_encode_memory.py/cal/20180515/2018-5-15;12-20-3.txt"
# timefile="/home/foranw/src/tasks/mgs_encode_memory.py/cal/20180515/s1_timing_122100.txt"
if len(sys.argv) <= 2:
    import wx
    app = wx.App()
    frame = wx.Frame(None, -1, "score calibratation")
    eyefile_dlg = wx.FileDialog(frame, "eye file")
    eyefile_dlg.ShowModal()
    eyefile = eyefile_dlg.GetPath()
    # optinal timing file
    timefile_dlg = wx.FileDialog(frame, "timing file")
    timefile_dlg.ShowModal()
    timefile = eyefile_dlg.GetPath()
else:
    eyefile = sys.argv[1]
    if len(sys.argv) >= 3:
        timefile = sys.argv[2]

if eyefile is None:
    os.exit(1)


raw_df = read_arrington(eyefile)
if timefile is None:
    df = et_3part_trigger(raw_df)
else:
    df = add_cal_timing(timefile, raw_df)

gzcol = 'x_correctedgaze'

df.boxplot(column=[gzcol], by=['pos', 'onset_rank'], rot=90)
plt.show()

df['diff'] = df[gzcol].diff()
tplot = df.query("diff < .01").plot.scatter(gzcol, 'totaltime')
# set x bounds to not show way off saccades
tplot.axis([0, 1.2, -1, max(df.totaltime)+1])

# code from eye drawing
pos = pd.np.linspace(.1, .9, 20)
allpos = pd.np.concatenate([pos, -1 * pos])
# [ -1 -> 1 ] --> [0 1]
for x in (allpos + 1)/2:
    plt.axvline(x=x, color='k', linestyle='--')
plt.show()

# m = df.groupby(['pos'])['x_gaze'].mean()
# smry = df.groupby(['pos'])['x_gaze'].\
#        agg({'m':lambda x: pd.np.mean(x), 's': lambda x: pd.np.std(x)})

smry = df.groupby(['pos'])[gzcol].agg(['mean', 'std'])
smry.plot()
plt.show()

sys.exit(0)
# --- for a file that does not have triggers
# df.\
#     assign(onset=df.event_onset).\
#     groupby(['pos','event_onset'])['onset'].\
#     apply(len)
#   ==> 46 is samples per event

eyefile = "/mnt/usb/kevin_20180509.txt"
kdf = read_arrington(eyefile)
tplot = kdf.query("diff < .01").plot.scatter(gzcol, 'totaltime')
# set x bounds to not show way off saccades
tplot.axis([0, 1.2, -1, max(kdf.totaltime)+1])

# code from eye drawing
pos = pd.np.linspace(.1, .9, 20)
allpos = pd.np.concatenate([pos, -1 * pos])
# [ -1 -> 1 ] --> [0 1]
for x in (allpos + 1)/2:
    plt.axvline(x=x, color='k', linestyle='--')
plt.show()


import seaborn as sns

gzcol = 'x_correctedgaze'

df.boxplot(column=[gzcol], by=['pos', 'onset_rank'], rot=90)
#ax = sns.boxplot(x=gzcol,
