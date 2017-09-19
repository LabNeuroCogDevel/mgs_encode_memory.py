#!/usr/bin/env python2

from __future__ import division
import numpy,math,numpy.matlib,random,numpy.random

'''
 shuf_for_ntrials creates a shuffled vector repeated to match the number of trials
'''
def shuf_for_ntrials(vec,ntrials):
  n=int(math.ceil( float(ntrials)/len(vec) ))
  mat=numpy.matlib.repmat(vec,1, n).flatten()
  numpy.random.shuffle(mat)
  return(mat[:ntrials])

# we could  img.units='deg', but that might complicate testing on diff screens
def ratio(screen,image,scale): return(float(screen) * scale/float(image))

'''
 replace_img adjust the image and position of a psychopy.visual.ImageStim
'''
def replace_img(img,filename,horz,imgpercent=.04):
  # set image, get props
  img.image=filename
  (iw,ih) = img._origSize
  (sw,sh) = img.win.size

  img.units='pixels'
  
  # resize img
  scalew= ratio(sw,iw,imgpercent)
  #scaleh= ratio(sh,ih,imgpercent) 
  # scale evenly in relation to x-axis
  img.size=(scalew*iw,scalew*sw/sh*ih) 

  ## position
  winmax=sw/float(2)
  # -1 => -400 for 800 wide screen
  horzpos=horz*winmax
  halfimgsize=scalew*iw/2.0
  # are we partially off the screen? max edges perfect
  if   horzpos - halfimgsize < -winmax :
      horzpos = halfimgsize - winmax
  elif horzpos + halfimgsize > winmax:
      horzpos = winmax - halfimgsize
  # set
  img.pos=(horzpos,0)

  ## draw
  img.draw()
