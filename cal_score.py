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


# --- read in a calibration file
# adapted from perl:
# BEGIN{$event="NA\\tNA"}
#  $event="$F[2]\\t$F[1]" if/^12/;
#  print join("\\t",@F[1..12],$event) if m/^10/'
def read_arrington(eyefile):
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
    return(df)
def et_3part_trigger(df):
   # event like ["fix_center_0.5", "look_Left_-0.605...",...] => separate columns, pos should be numeric
   df['action'], df['side'], df['pos'] = df['event_str'].str.split('_',2).str
   df['pos'] = df['pos'].replace('None',pd.np.Inf).astype('float')
   
   
   # show box plot of each positions
   df['pos'] = ["%.02f" % x for x in df['pos']]
   df = df.query('pos not in ["nan", "inf"] ')
   df['onset_rank'] = df.groupby('pos')['event_onset'].rank(method="dense").astype(int)
   df.loc[df.onset_rank>=3,'onset_rank'] = 3

   return(df)

df = read_arrington(eyefile)
df = et_3part_trigger(df)

gzcol = 'x_correctedgaze'

df.boxplot(column=[gzcol],by=['pos','onset_rank'],rot=90)
plt.show()


kdf['diff'] =kdf[gzcol].diff()
tplot = df.query("diff < .01").plot.scatter(gzcol,'totaltime')
# set x bounds to not show way off saccades
tplot.axis([0,1.2,-1,max(df.totaltime)+1])

# code from eye drawing
pos = pd.np.linspace(.1, .9, 20)
allpos = pd.np.concatenate([pos, -1 * pos])
# [ -1 -> 1 ] --> [0 1]
for x in (allpos + 1)/2:
    plt.axvline(x=x, color='k', linestyle='--')
plt.show()

#m = df.groupby(['pos'])['x_gaze'].mean()
#smry = df.groupby(['pos'])['x_gaze'].agg({'m':lambda x: pd.np.mean(x), 's': lambda x: pd.np.std(x)})
smry = df.groupby(['pos'])[gzcol].agg(['mean','std'])

smry.plot()
plt.show()


## for a file that does not have triggers
# df.assign(onset=df.event_onset).groupby(['pos','event_onset'])['onset'].apply(len) ==> 46 is samples per event
eyefile = "/mnt/usb/kevin_20180509.txt"
kdf = read_arrington(eyefile)
tplot = kdf.query("diff < .01").plot.scatter(gzcol,'totaltime')
# set x bounds to not show way off saccades
tplot.axis([0,1.2,-1,max(kdf.totaltime)+1])

# code from eye drawing
pos = pd.np.linspace(.1, .9, 20)
allpos = pd.np.concatenate([pos, -1 * pos])
# [ -1 -> 1 ] --> [0 1]
for x in (allpos + 1)/2:
    plt.axvline(x=x, color='k', linestyle='--')
plt.show()

# ideal
np=pd.np
def sim_to_pos(x,noise=.02):
    gen_noise = lambda n: np.random.normal(-1*noise,noise,n)
    center = 0
    to_x = np.linspace(center,x,10) + gen_noise(10)
    fix_x = x + gen_noise(36)
    away_x = np.linspace(x,center,10) + gen_noise(10)
    fix = center + gen_noise(36)
    return( to_x.tolist() + fix_x.tolist() + away_x.tolist() + fix.tolist() )
          

freq=60.0 # other is 16?
allpos_ts = allpos[pd.np.random.permutation(len(allpos))] 
ideal_ts = np.array([[sim_to_pos(x),sim_to_pos(x)] for x in allpos_ts ]). reshape(1,len(allpos)*46*2*2)[0]
idf = pd.DataFrame( {'x_correctedgaze': (ideal_ts+1)/2, 'totaltime':[1/freq*x for x in range(len(ideal_ts))]})

tplot = idf.plot.scatter(gzcol,'totaltime')
for x in (allpos+1)/2:
    plt.axvline(x=x, color='k', linestyle='--')
plt.show()

# -- show with gui
#wxlv = wx.ListCtrl(frame, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
#wxlv.SetColumns([
#    olv.ColumnDefn('pos','
