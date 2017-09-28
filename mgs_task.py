#!/usr/bin/env python2

from __future__ import division
import numpy, math, numpy.matlib, random, numpy.random
from psychopy import visual, core,  event, logging

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
just like core.wait, but instead of waiting a duration
we wait until a stoptime.
optional maxwait will throw an error if we are wating too long 
so we dont get stuck. defaults to 30 seconds
"""
def wait_until(stoptime,maxwait=30):
  if stoptime - core.getTime()  > maxwait:
    raise ValueError("requiest to wait until stoptime is more than 30 seconds, secify maxwait to avoid this error")
  # will hog cpu -- no pyglet.media.dispatch_events here
  while core.getTime() < stoptime:
    continue
   
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

class mgsTask:
   # initialize all the compoents we need
   def __init__(self,win,accept_keys={'known':'k', 'unknown': 'd', 'left':'d','right':'k', 'oops':'o' }):
      self.win=win
      self.accept_keys=accept_keys
      self.img = visual.ImageStim(win,name="imgdot") #,AutoDraw=False)
      self.timer = core.Clock()
      
      # could have just one and change the color
      self.iti_fix = visual.TextStim(win, text='+',name='iti_fixation',color='white')
      self.isi_fix = visual.TextStim(win, text='+',name='isi_fixation',color='yellow')
      self.trg_fix = visual.TextStim(win, text='+',name='trg_fixation',color='red')
      
      ## for quiz
      self.text_KU = visual.TextStim(win, text='unkown or known',name='KnownUnknown',color='white',pos=(0,-.75))
      self.text_LR = visual.TextStim(win, text='left or right',name='LeftRight',color='white',pos=(0,-.75))
      
      self.dir_key_text   = [ (self.accept_keys['left'] , 'left         '),\
                              (self.accept_keys['right'], '        right'),\
                              (self.accept_keys['oops'] , '    oops     ')]
      self.known_key_text = [ (self.accept_keys['known']  , '           known'),\
                              (self.accept_keys['unknown'], 'unknown         ') ]



   """
   simple iti. flush logs 
   globals:
     iti_fix visual.TextStim
   """
   def run_iti(self,iti=0):
       self.iti_fix.draw(); self.win.flip(); 
       logging.flush();
       if(iti>0): core.wait(iti)
   
   """
   saccade trial
    globals:
     win, trg_fix, isi_fix
   """
   def sacc_trial(self,imgfile,horz,starttime=0): 
       if(starttime==0): starttime=core.getTime()
       trgon=starttime;
       imgon=trgon+.5
       ision=imgon+.5
       sacon=ision+.5
   
       # get ready red target
       self.trg_fix.draw()
       wait_until(trgon); self.win.flip()
   
       # show an image
       replace_img(self.img,imgfile,horz,.05)
       wait_until(imgon); self.win.flip()
       
       # back to fix
       self.isi_fix.draw()
       wait_until(ision); self.win.flip()
   
       # memory guided                                                 
       # -- empty screen nothing to draw
       wait_until(sacon); self.win.flip()
   
       # coded with wait instead of wait_until:
       ## get ready
       #trg_fix.draw(); win.flip(); core.wait(0.5)
       ## visual guided
       #replace_img(img,imgfile,horz,.05); win.flip(); core.wait(.5) 
       ## back to fix
       #isi_fix.draw(); win.flip(); core.wait(0.5)
       ## memory guided
       #win.flip(); core.wait(.5)
   
   """
   record button response  and reaction time
   display equally long for regardless of RT
   provide feedback after push
   globals:
     win
   """
   def key_feedback(self,keys_text_tupple,feedback,timer,maxtime=1.5):
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
           self.win.flip();
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
   def recall_trial(self,imgfile): 
       # draw the image and the text (keep image on across flips)
       replace_img(self.img,imgfile,0,.25)
       self.img.setAutoDraw(True)
       self.text_KU.draw()
       self.win.flip() 
       
       self.timer.reset();
       # do we know this image?
       (knowkey,knowrt) = self.key_feedback( self.known_key_text, self.text_KU, self.timer,1.5)
       # end early if we have not seen this before
       if( knowkey != self.accept_keys['known']): return( (knowkey,None), (knowrt,None) )
   
       # othewise get direction
       self.text_LR.draw(); self.win.flip()
       (dirkey,dirrt) = self.key_feedback( self.dir_key_text, self.text_LR, self.timer,1.5)
   
       self.img.setAutoDraw(False);
       return( (knowkey,dirkey), (knowrt,dirrt) )
