#!/usr/bin/env python3
import mne
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
testfile = 'Orma-MGS.bdf'

d = mne.io.read_raw_edf(testfile)
d.ch_names # EGX8 == 135 | Status == 143

# get "Status" channel
# initial values
#remove min to get actual values sent
start, stop = d.time_as_index([100,200])
data, times = d[143,:]
data = data[0,:]
data = data - data.min()
# remove way to hight start values 
data[data > 260 ] = 0

# hacky: make a raw array to use find_events
# instead of doing our own 
toadd_info = mne.create_info(['stim'],d.info['sfreq'])
toadd_info['lowpass'] = d.info['lowpass']
toadd = mne.io.RawArray(data.reshape((1,data.shape[0])),toadd_info)
e = mne.find_events(toadd,stim_channel='stim')

sorted(np.diff(e[:,0])/toadd_info['sfreq'])

# more exact compare 
def hist_dur(d, e1='cue', e2='vgs'):
    a=edf_wide[e2] - edf_wide[e1]
    a=a[np.isfinite(a)] 
    plt.hist(abs(a))
    plt.title('%s - %s' % (e2,e1) )
    plt.savefig('imgs/%s_%s.png' % (e2,e1) )
    plt.gcf().clear()

# get a dataframe, identify the event  and pivot to long for diffs 
edf = pd.DataFrame({'ttl': e[:,2],'onset': e[:,0]/d.info['sfreq']})
edf['trial'] = np.cumsum(edf.ttl == 254 )
edf['event'] = pd.cut(edf.ttl,(0,100,150,200,250,300),labels=['cue','vgs','isi','mgs','iti'])
edf_wide =  edf.pivot(index='trial',columns='event',values='onset')

if not os.path.exists('imgs'):
    os.makedirs('imgs')

hist_dur(edf_wide, 'iti', 'cue')
hist_dur(edf_wide, 'cue', 'vgs')
hist_dur(edf_wide, 'vgs', 'isi')
hist_dur(edf_wide, 'isi', 'mgs')

