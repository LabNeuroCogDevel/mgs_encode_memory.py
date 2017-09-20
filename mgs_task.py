#!/usr/bin/env python2

from __future__ import division
import numpy,math,numpy.matlib,random,numpy.random

'''
 shuf_for_ntrials creates a shuffled vector repeated to match the number of trials
'''
def shuf_for_ntrials(vec,ntrials):
  nitems=len(vec)
  if nitems == 0 or ntrials == 0: return([])

  items_over= ntrials % nitems
  nfullvec = int(math.floor( ntrials/nitems))
  # have 3 items want 5 trials
  # nfullvec=1; items_over=2

  # repeat full vector as many times as we can
  mat=numpy.matlib.repmat(vec,1, nfullvec).flatten()
  # then add a truncated shuffled vector as needed
  if items_over>0:
    numpy.random.shuffle(vec)
    mat=numpy.append(mat,vec[:items_over])

  numpy.random.shuffle(mat)
  return(mat)

# we could  img.units='deg', but that might complicate testing on diff screens
def ratio(screen,image,scale): return(float(screen) * scale/float(image))

"""
create stimlist for saccade trials.
expects allimages to be unique list (no repeats)
images will be repeated if needed (ntrial>nimags), but postion will be constant for each image
"""
def gen_stimlist(allimages,possiblepos,ntrials):
   ## generate positions and images order
   # match positions to an image
   nimages=len(allimages)
   positions=shuf_for_ntrials(possiblepos,nimages )
   imgpos = { allimages[i]: positions[i] for i in range(nimages) }
   imgfiles = shuf_for_ntrials( allimages, ntrials)
   
   
   stimList = [ {'imgfile': imgfiles[i], 'horz': imgpos[imgfiles[i]] } for i in range(ntrials) ]
   return(stimList)

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
  #img.size=(scalew*iw,scalew*sw/sh*ih) # if units were 'norm'
  img.size=(scalew*iw,scalew*ih) # square pixels
  # img._requestedSize => (80,80) if imgprecent=.1*sw=800

  ## position
  winmax=sw/float(2)
  # horz=-1 => -400 for 800 wide screen
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
