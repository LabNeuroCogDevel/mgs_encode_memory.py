#!/usr/bin/env python2
# -*- py-which-shell: "python2"; -*-

from __future__ import division
import numpy, math, numpy.matlib, random, numpy.random
from psychopy import visual, core,  event, logging
import glob,re,os

# this causes some artifacts!?
def take_screenshot(win,name):
  if not os.path.exists('screenshots/'): os.mkdir('screenshots')
  win.getMovieFrame()   # Defaults to front buffer, I.e. what's on screen now.
  win.saveMovieFrames('screenshots/' + name +'.png')

"""
generate example timing
"""
def make_timing():
  tr=1.5
  ITI=numpy.array([6,5,6,3,6,2,6,3,2,3,5,7,5,3,4,2,5,3,5,8]) *tr
  delay= [4]*10 + [5] *7 + [6]*3
  delay=numpy.array(delay)*tr
  numpy.random.shuffle(delay)
  curtime=1
  tonsets=[]
  sonsets=[]
  for i in range(len(ITI)):
    tonsets.append( curtime)
    curtime += 1.5 + 1.5 + delay[i] # cue + target + delay
    sonsets.append(curtime)
    curtime += 1.5 + ITI[i] # MGS + ITI
  # only one type of mgs
  with open('stims/example_00002_02_mgs.1D','w') as f:
    f.write(" ".join([ "%.02f"%x for x in sonsets ]))

  # write different types of cue
  type_names=['A','B','C','none']
  n_types=len(type_names)
  n_on = len(tonsets)
  idx = [x for x in range(0,n_on) ]
  step = int(n_on/n_types)
  numpy.random.shuffle(idx)
  
  for i,t in enumerate(type_names):
      si = i*step
      se = (i+1)*step
      if i == n_types: se=n_on
      with open('stims/example_00002_01_cue_cat'+t+'.1D','w') as f:
        f.write(" ".join([ "%.02f"%x for x in tonsets[si:se] ]))

  return( (tonsets,sonsets))
  
"""
read onsets files given a pattern. will append *1D to pattern
everything not in pattern is stripped from returned onset dict
   # input looks like
   with open('stims/example_0001_01_cue.1D','w') as f: f.write(" ".join([ "%.02f"%x for x in numpy.cumsum(.5+numpy.repeat(2,10) ) ]));
"""
def read_timing(onsetprefix):
  onsetdict = {}
  onsetfiles = glob.glob(onsetprefix + '*1D')
  if(len(onsetfiles)<=0):
    print('no files in %s'%onsetprefix)
    raise Exception('bad files')
  for onset1D in onsetfiles:
    # key name will be file name but 
    # remove the last 3 chars (.1D) and the glob part
    onsettype=onset1D[:-3].replace(onsetprefix,'')
    with open(onset1D) as f:
        onsetdict[onsettype] = [ float(x) for x in f.read().split() ]
  return(onsetdict)

def image_sets():
  allimages=glob.glob('img_circle/*png')
  ## break images into saccade images and novel (for memory quiz)
  novelfile=re.compile('.*\.01\..*') # any .01. image
  sacc_images = [ x for x in allimages if not novelfile.match(x) ]
  novel_images = [ x for x in allimages if novelfile.match(x) ]
  return( (sacc_images, novel_images) )

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
  return(img.pos)

"""
create stimlist for saccade trials.
expects allimages to be unique list (no repeats)
images will be repeated if needed (ntrial>nimags), but postion will be constant for each image
"""
def gen_stimlist(allimages,possiblepos,onsetsprefix):
   # read in onset times, curerntly just the start of the trial
   onsets = read_timing(onsetsprefix)
   print(onsetsprefix)
   print(onsets)
   ## generate positions and images order
   # match positions to an image
   ntrials = len(onsets['01_cue'])
   nimages=len(allimages)
   positions=shuf_for_ntrials(possiblepos,nimages )
   imgpos = { allimages[i]: positions[i] for i in range(nimages) }
   imgfiles = shuf_for_ntrials( allimages, ntrials)

   # what types of cues do we have
   cues = [ x.replace('_01_cue_','') for x in onsets.keys() if re.match('_01_cue',x) ]
   # cueon=[]
   # for k in cues:
   #   for x in onsets['_01_cue_'+k]:
   #      cueon.append( (k,x) )
   # same as above
   [(k,x) for k in cues for x in onsets['_01_cue_'+k]]
   cueon.sort(key=lambda x:  x[1])

   stimList = [
      {'imgfile': imgfiles[i],
       'horz': imgpos[imgfiles[i]],
       #'01_cue': onsets['01_cue'][i], # when it was just one cue type
       'cuetype': cueon[i][0],
       '01_cue': cueon[i][1],
       '02_mgs': onsets['02_mgs'][i]
      } for i in range(ntrials) ]

   return(stimList)

class mgsTask:
   # initialize all the compoents we need
   def __init__(self,win,accept_keys={'known':'k', 'unknown': 'd', 'left':'d','right':'k', 'oops':'o' }):
      # settings for eyetracking and parallel port ttl (eeg)
      self.vpxDll = "C:/ARI/VP/VPX_InterApp.dll"
      self.pp_adress = 0x0378 # see also 0x03BC, LPT2 0x0278 or 0x0378, LTP 0x0278

      # images relative to screen size
      self.imgratsize=.15

      # window and keys
      self.win=win
      self.accept_keys=accept_keys

      # allocate screen parts 
      self.img = visual.ImageStim(win,name="imgdot") #,AutoDraw=False)
      self.crcl = visual.Circle(win,radius=10,lineColor=None,fillColor='yellow',name="circledot") #,AutoDraw=False)
      self.crcl.units='pix'

      self.timer = core.Clock()
      
      # could have just one and change the color
      self.iti_fix = visual.TextStim(win, text='+',name='iti_fixation',color='white')
      self.isi_fix = visual.TextStim(win, text='+',name='isi_fixation',color='yellow')
      self.cue_fix = visual.TextStim(win, text='+',name='cue_fixation',color='red')
      self.textbox = visual.TextStim(win, text='**',name='generic_textbox',alignHoriz='left',color='white',wrapWidth=2)
      
      ## for quiz
      self.text_KU = visual.TextStim(win, text='kown or unknown',name='KnownUnknown',color='white',pos=(0,-.75))
      self.text_LR = visual.TextStim(win, text='left or right',name='LeftRight',color='white',pos=(0,-.75))
      
      self.dir_key_text   = [ (self.accept_keys['left'] , 'left         '),\
                              (self.accept_keys['right'], '        right'),\
                              (self.accept_keys['oops'] , '    oops     ')]
      self.known_key_text = [ (self.accept_keys['known']  , 'known           '),\
                              (self.accept_keys['unknown'], '         unknown') ]

   """
   send a trigger on parallel port (eeg) or ethernet (eyetracker)
   in MR, we do eyetracking, and want to send a trigger to the tracker
   in EEG, we dont have eye tracking, but want to annotate screen flips
   """
   def send_code(self,ttlstr):
      # TODO: TEST SOMEWHERE
      if(self.usePP):
        # initialize parallel port
        if not hasattr(send_code,'port'):
          from psychopy import parallel
          send_code.port = parallel.ParallelPort(address=self.ppaddress)
          send_code.d = {
            'iti' = 255,
            'cue' = 1,
            'img' = 2,
            'img_inside' = 3,
            'img_outside_natural' = 4,
            'img_outside_made' = 5,
            'img_outside_none' = 6,
            'isi' = 200,
            'mgs' = 10,
            'mgsLeftFar' = 12,
            'mgsLeftCenter' = 13,
            'mgsRightCenter' = 14,
            'mgsRightFar' = 15
          }
            
        # send code, or 100 if cannot find
        send_code.port.setData(send_code.d.get(ttlstr,100))

      # see also: vpx.VPX_GetStatus(VPX_STATUS_ViewPointIsRunning) < 1
      if(self.useArrington):
        # initialze eyetracking
        if not hasattr(send_code,'vpx'):
          #vpxDll="C:/ARI/VP/VPX_InterApp.dll"
          if not os.access(self.vpxDll,os.F_OK):
            Exception('cannot find eyetracking dll @ '+vpxDll)
          vpx = CDLL( cdll.LoadLibrary(vpxDll) )
          if vpx.VPX_GetStatus(VPX_STATUS_ViewPointIsRunning) < 1:
            Exception('ViewPoint is not running!')
        vpx.VPX_SendCommand('dataFile_InsertString "%s"'%ttlstr)
        # TODO start with setTTL? see manual ViewPoint-UserGuide-082.pdf 
      if(self.verbose):
        print("sent code %s"%ttlstr)
        

   """
   wait for scanner trigger press
   return time of keypush
   """
   def wait_for_scanner(self,trigger):
       self.textbox.pos=(-1,0)
       self.textbox.setText('Waiting for scanner (pulse trigger)'%trigger)
       self.textbox.draw()
       self.win.flip()
       event.waitKeys(keyList=trigger)
       starttime=core.getTime()
       self.run_iti()
       return(starttime)

   """
   simple iti. flush logs 
   globals:
     iti_fix visual.TextStim
   """
   def run_iti(self,iti=0):
       self.iti_fix.draw();
       self.send_code('iti')
       self.win.flip(); 
       logging.flush();
       if(iti>0): core.wait(iti)
   
   """
   saccade trial
    globals:
     win, cue_fix, isi_fix
   """
   def sacc_trial(self,imgfile,horz,starttime=0,mgson=0,takeshots=None): 
       if(starttime==0): starttime=core.getTime()
       cueon=starttime;
       imgon=cueon+1.5
       ision=imgon+1.5

       #if takeshots: take_screenshot(self.win,takeshots+'_00_start')

       if(mgson ==0): mgson=ision+1.5
       mgsoff=mgson+1.5
   
       # get ready red target
       self.cue_fix.draw()
       wait_until(cueon)
       self.send_code('cue')
       self.win.flip()
       if takeshots: take_screenshot(self.win,takeshots+'_01_cue')
   
       # show an image
       if not imgfile == None:
         imgpos=replace_img(self.img,imgfile,horz,self.imgratsize)
       self.crcl.pos=imgpos
       self.crcl.draw()
       wait_until(imgon);
       self.send_code('img')
       self.win.flip()
       if takeshots: take_screenshot(self.win,takeshots+'_02_imgon')
       
       # back to fix
       self.isi_fix.draw()
       wait_until(ision);
       self.send_code('isi')
       self.win.flip()
       if takeshots: take_screenshot(self.win,takeshots+'_03_isi')
   
       # memory guided (recall)
       # -- empty screen nothing to draw
       wait_until(mgson);
       self.send_code('mgs')
       self.win.flip()
       if takeshots: take_screenshot(self.win,takeshots+'_04_mgs')
       wait_until(mgsoff)
   
       # coded with wait instead of wait_until:
       ## get ready
       #cue_fix.draw(); win.flip(); core.wait(0.5)
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
       if( knowkey != self.accept_keys['known']):
         self.img.setAutoDraw(False);
         return( (knowkey,None), (knowrt,None) )
   
       # we think we remember this image, do we remember where it was
       self.text_LR.draw(); self.win.flip()

       self.timer.reset();
       (dirkey,dirrt) = self.key_feedback( self.dir_key_text, self.text_LR, self.timer,1.5)
   
       self.img.setAutoDraw(False);
       return( (knowkey,dirkey), (knowrt,dirrt) )

   """
   quick def to flip, stall half a second, and wait for any key
   """
   def instruction_flip(self): self.win.flip();core.wait(.4);event.waitKeys()

   """
   saccade task instructions
   """
   def sacc_instructions(self):

       self.textbox.pos=(-.9,0)
       self.textbox.text = \
          '1. When the image appears, look at it. Remember where you looked\n' + \
          '2. Look at the + in the center when the image goes away\n' + \
          '3. Look where the image was when the + goes away\n' + \
          'Hint: The + will be red before an image appears.\n' + \
          'Hint: The + will be yellow before you have to look where an image was'
           
       self.textbox.draw()
       self.instruction_flip()

       self.textbox.pos=(-.9,.9)
       self.textbox.text='target: get ready to look at an image'
       self.textbox.draw()
       self.cue_fix.draw()
       self.instruction_flip()

       self.textbox.text='image: look at the dot on top of the image'
       imgpos=replace_img(self.img,'img_circle/winter.02.png',1,self.imgratsize)
       self.textbox.draw()
       self.crcl.pos=imgpos
       self.crcl.draw()
       self.instruction_flip()

       self.textbox.text='wait: go back to center'
       self.textbox.draw()
       self.isi_fix.draw()
       self.instruction_flip()

       self.textbox.text='recall: look to where image was'
       self.textbox.draw()
       self.instruction_flip()

       self.textbox.text='relax: wait for the red cross to signal a new round'
       self.textbox.draw()
       self.iti_fix.draw()
       self.instruction_flip()
       self.textbox.pos=(0,0)
    
