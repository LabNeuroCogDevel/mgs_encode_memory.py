#!/usr/bin/env python2

from __future__ import division
import numpy, math, numpy.matlib, random, numpy.random

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


"""
evaluate known/unkown and left/right based on position and accept_keys
position==nan means it was never seen
neg. position is left, positive position is right
"""
def response_should_be(pos,accept_keys):
    if(math.isnan(pos )): return( (accept_keys['unknown'],accept_keys['oops']) )
    elif( pos < 0): return( (accept_keys['known'],accept_keys['left']) ) 
    elif( pos > 0): return( (accept_keys['known'],accept_keys['left'])  )
    else: raise ValueError('bad pos?! how!?')
"""
simple iti. flush logs 
globals:
  iti_fix visual.TextStim
"""
def run_iti(iti):
    iti_fix.draw(); win.flip(); 
    logging.flush(); core.wait(iti)

"""
saccade trial
 globals:
  win, trg_fix, isi_fix
"""
def sacc_trial(imgfile,horz): 
    # get ready
    trg_fix.draw(); win.flip(); core.wait(0.5)
    # visual guided
    replace_img(img,imgfile,horz,.05); win.flip(); core.wait(.5) 
    # back to fix
    isi_fix.draw(); win.flip(); core.wait(0.5)
    # memory guided
    win.flip(); core.wait(.5)

"""
record button response  and reaction time
display equally long for regardless of RT
provide feedback after push
globals:
  win
"""
def key_feedback(keys_text_tupple,feedback,timer,maxtime=1.5):
    validkeys= [ x[0] for x in keys_text_tupple ]
    origtext=feedback.text

    # get list of tuple (keypush,rt)
    t=event.waitKeys(keyList=validkeys,maxWait=maxtime,timeStamped=timer )
    # we're only going to look at single button pushes (already only accepting 2 or 3 keys)
    if(t != None and len(t)==1):
        (keypressed,rt)=t[0]
        for (k,txt) in keys_text_tupple:
            if(keypressed == k): # todo, allow multple keys?
                feedback.text=txt
                break

        feedback.draw();
        win.flip();
        feedback.text=origtext
    # no response or too many responses means no keypress and no rt
    else:
        t=[(None,None)]
    # wait to finish
    while(timer.getTime() < maxtime ): pass
    # give key and rt
    return(t[0])

    
"""
run a recall trial. 
globals:
 img, text_KU, text_LR, dir_key_text, known_key_text
"""
def recall_trial(imgfile,keys): 
    replace_img(img,imgfile,0,.25);img.setAutoDraw(True); text_KU.draw(); win.flip(); 
    timer.reset();
    # do we know this image?
    (knowkey,knowrt) = key_feedback( known_key_text, text_KU, timer,1.5)
    # end early if we have not seen this before
    if( knowkey != accept_keys['known']): return( (knowkey,None), (knowrt,None) )

    # othewise get direction
    (dirkey,dirrt) = key_feedback( dir_key_text, text_LR, timer,1.5)

    img.setAutoDraw(False);
    return( (knowkey,dirkey), (knowrt,dirrt) )
