#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd

d = pd.read_excel('hierarchy_three_levels/three_levels.xlsx',skiprows=1)

d_txt = d.\
 melt(id_vars=['category','indoor','outdoor, natural','outdoor, man-made'],var_name='specific').\
 query('value==1').\
 drop(['value']).\
 melt(id_vars=['category','specific'],var_name='generic').\
 query('value==1').\
 filter(['category','specific','generic'])
d_txt.to_csv('levels.txt',sep="\t",doublequote=False,index=F)
