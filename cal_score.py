#!/usr/bin/env python2
import wx
import os
import pandas as pd
import matplotlib.pyplot as plt

# open a file
app = wx.App()
frame = wx.Frame(None, -1, "score calibratation")
eyefile_dlg = wx.FileDialog(frame, "File")
eyefile_dlg.ShowModal()
eyefile = eyefile_dlg.GetPath()
if eyefile is None:
    os.exit(1)

wxlv = wx.ListCtrl(frame, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

# --- read in a calibration file
# adapted from perl:
# BEGIN{$event="NA\\tNA"}
#  $event="$F[2]\\t$F[1]" if/^12/;
#  print join("\\t",@F[1..12],$event) if m/^10/'
with open(eyefile) as f:
    event = None
    event_time=0
    data = []
    for line in f:
        v = line.split()
        # line starts with 10, it's data
        #                  12, it's event info
        if v[0] == "10":
            data.append([ float(x) for x in v[1:13] ] + [event,event_time])
        elif v[0] == "12":
            event = v[2]
            event_time = float(v[1])
        else:
            pass
            #print("Bad line " + line) 

df = pd.DataFrame(data)
df.columns=["totaltime", "deltatime",
            "x_gaze", "y_gaze", "x_correctedgaze", "y_correctedgaze",
            "region", "pupilwidth", "pupilheight", "quality",
            "fixation", "count", "event_str", "event_onset"]
# event like ["fix_center_0.5", "look_Left_-0.605...",...] => separate columns, pos should be numeric
df['action'], df['side'], df['pos'] = df['event_str'].str.split('_',2).str
df['pos'] = df['pos'].replace('None',pd.np.Inf).astype('float')

#m = df.groupby(['pos'])['x_gaze'].mean()
#smry = df.groupby(['pos'])['x_gaze'].agg({'m':lambda x: pd.np.mean(x), 's': lambda x: pd.np.std(x)})
smry = df.groupby(['pos'])['x_gaze'].agg(['mean','std'])

smry.plot()
plt.show()


# -- show with gui
#wxlv.SetColumns([
#    olv.ColumnDefn('pos','
