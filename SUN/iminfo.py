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

# brigtness
# enorm with brightness weights: .241,.691,.086
# method no. 3 from
# https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
def precieve_brightness(imgarr):
    weights=[.241,.691,.068]
    m=imgarr.mean(axis=0) # average r g an b
    mbyp=zip(m,weights )
    esum=[ p*(v**2) for v,p in mbyp ]
    enorm=np.sum(esum)**(1/2)
    return(enorm)

def rgb_ratio(imgarr,pallete):
    p    = pairwise_distances_argmin(imgarr,pallete)
    # bins like 0 to 1 (exclude), 1 to 2 (exclude)
    bins = np.histogram(p, bins=range( len(pallete)+1)  ) [0]
    return(bins/np.sum(bins))


def imginfo(imgf,pallete):
   try:
     img = imread(imgf)
     return(imginfo_(img, pallete))
   except Exception as e:
     return(np.append([0,0,0], [0]*len(pallete)) )

def imginfo_(img,pallete):
   try:
     w,h,d = img.shape
     imgarr = np.reshape(img,(w*h,d))
     bins=rgb_ratio(imgarr,pallete)
     bright=precieve_brightness(imgarr)
     return( np.append([w,h,bright],bins) )
   except Exception as e:
     print(e)
     return(np.append([0,0,0], [0]*len(pallete)) )

if __name__ == "__main__":
    l = pd.read_csv('./levels.txt',sep="\t")
    
    #rgbbw = np.array([ [1,0,0],[0,1,0],[0,0,1],[0,0,0],[1,1,1] ])*255
    rgb = np.array([ [1,0,0],[0,1,0],[0,0,1]])*255
    bw = np.array([ [0,0,0],[1,1,1]])*255
    
    #allimglist = glob('SUN397/*/*/*.jpg')
    
    d=[]
    for idx, row in l.iterrows():
     print(row['category'])
     allimglist = glob('SUN397/'+row['category']+'/*.jpg')
     c= row.values
     print('\t%d images'%len(allimglist))
     t0=time.time()
     for imgf in allimglist:
       # make e.g. /j/jewelry_shop
       i=imginfo(imgf,rgb)
       row=np.append(imgf,np.append(c,i))
       d.append(row)
     dur=(time.time()-t0)
     print("\ttook %f m, %f s/img"%( dur/60, dur/len(allimglist) ) )
    
    df = pd.DataFrame(d)
    df.columns = ['file','cat','specific','generic','w','h','pbright','r','g','b']
    df.to_csv("info.txt",header=True,doublequote="",sep="\t",index=False)
    
    #quant  = np.array([ rgbbw[i] for i in p ],dtype=np.uint8).reshape(w,h,d)
    #plt.imshow(quant)
    #plt.show()
    
    
