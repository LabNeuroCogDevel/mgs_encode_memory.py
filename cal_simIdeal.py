#!/usr/bin/env python2
import pandas as pd
import matplotlib.pyplot as plt

#
# ideal eyetracking time series
#

np = pd.np

pos = pd.np.linspace(.1, .9, 20)
allpos = pd.np.concatenate([pos, -1 * pos])
gzcol = 'x_correctedgaze'


def gen_noise(n, noise):
    return(np.random.normal(-1*noise, noise, n))


def sim_to_pos(x, noise=.02):
    center = 0
    to_x = np.linspace(center, x, 10) + gen_noise(10)
    fix_x = x + gen_noise(36)
    away_x = np.linspace(x, center, 10) + gen_noise(10)
    fix = center + gen_noise(36)
    return(to_x.tolist() + fix_x.tolist() + away_x.tolist() + fix.tolist())


freq = 60.0  # other is 16?
allpos_ts = allpos[pd.np.random.permutation(len(allpos))]
ideal_ts = np.array([[sim_to_pos(x), sim_to_pos(x)] for x in allpos_ts]).\
           reshape(1, len(allpos)*46*2*2)[0]
idf = pd.DataFrame({gzcol:       (ideal_ts+1)/2,
                    'totaltime': [1/freq*x for x in range(len(ideal_ts))]})

tplot = idf.plot.scatter(gzcol, 'totaltime')
for x in (allpos+1)/2:
    plt.axvline(x=x, color='k', linestyle='--')
plt.show()
