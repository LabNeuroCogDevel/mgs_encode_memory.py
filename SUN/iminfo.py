#!/usr/bin/env python
# -*- coding: utf-8 -*-

# for each image: category size color
# needs: 
# * levels.txt from read.{R,py}
# * images in ./SUN397/
#
#

from imageio import imread 
from sklearn.metrics import pairwise_distances_argmin
import numpy as np
import pandas as pd
from glob import glob


def imginfo(imgf,pallete):
   try:
     img = imread(imgf)
     w,h,d = img.shape
     imgarr = np.reshape(img,(w*h,d))
     p    = pairwise_distances_argmin(imgarr,pallete)
     # bins like 0 to 1 (exclude), 1 to 2 (exclude)
     bins = np.histogram(p, bins=range( len(pallete)+1)  ) [0]
     return( np.append([w,h],bins) )
   except Exception as e:
     print(e)
     return(np.append([0,0], [0]*len(pallete)) )

l = pd.read_csv('./levels.txt',sep="\t")

rgbbw = np.array([ [1,0,0],[0,1,0],[0,0,1],[0,0,0],[1,1,1] ])*255
allimglist = glob('SUN397/*/*/*.jpg')

d=[]
for idx, row in l.iterrows():
 print(row['category'])
 allimglist = glob('SUN397/'+row['category']+'/*.jpg')
 c= row.values
 print('\t%d images'%len(allimglist))
 for imgf in allimglist:
   # make e.g. /j/jewelry_shop
   i=imginfo(imgf,rgbbw)
   row=np.append(imgf,np.append(c,i))
   d.append(row)



#import matplotlib.pyplot as plt
#quant  = np.array([ rgbbw[i] for i in p ],dtype=np.uint8).reshape(w,h,d)
#plt.imshow(quant)
#plt.show()


