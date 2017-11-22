#!/usr/bin/env python3
import os
import pandas as pd
from glob import glob

f = glob('SUN/circles/*txt')
d = pd.concat([pd.read_table(x, header=None, delimiter=" ").
               assign(f=x)
              for x in f])

# update df (remove height,widht, NA column (drop) )
# update f with no path or .txt
d.columns = ['h', 'w', 'p', 'r', 'g', 'b', 'drop', 'f']
d.drop(['h', 'w', 'drop'], 1, inplace=True)
d.f = [os.path.basename(x).replace('.txt', '') for x in d.f]

# subset
# np.mean(d.p) == 116.1, std == 26
q = d.query('abs(r-.33) < .1 and abs(g-.33) < .1 and abs(b-.33) <.1 and abs(p-116) < 10 ')

[os.link('SUN/circles/%s.png'%x,'SUN/circle_select/%s.png'%x) for x in q.f]
