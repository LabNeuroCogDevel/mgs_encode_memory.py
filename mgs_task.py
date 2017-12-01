#!/usr/bin/env python2
# -*- py-which-shell: "python2"; -*-

from __future__ import division
import numpy
import math
import numpy.matlib
import numpy.random
from psychopy import visual, core,  event, logging
import glob
import re
import os
import pandas
import numpy
import pickle


# this causes some artifacts!?
def take_screenshot(win, name):
    if not os.path.exists('screenshots/'):
        os.mkdir('screenshots')
    win.getMovieFrame()   # Defaults to front buffer, I.e. what's on screen now
    win.saveMovieFrames('screenshots/' + name + '.png')


def make_timing():
    """
    generate example timing
    """
    tr = 1.5
    ITI = numpy.array([6,5,6,3,6,2,6,3,2,3,5,7,5,3,4,2,5,3,5,8]) *tr
    delay = [4]*10 + [5] * 7 + [6]*3
    delay = numpy.array(delay)*tr
    numpy.random.shuffle(delay)
    curtime = 1
    tonsets = []
    sonsets = []
    for i in range(len(ITI)):
        tonsets.append(curtime)
        curtime += 1.5 + 1.5 + delay[i]  # cue + target + delay
        sonsets.append(curtime)
        curtime += 1.5 + ITI[i]  # MGS + ITI
        # only one type of mgs
    with open('stims/example_00002_02_mgs.1D', 'w') as f:
        f.write(" ".join(["%.02f" % x for x in sonsets]))

    # write different types of cue
    type_names = ['A', 'B', 'C', 'none']
    n_types = len(type_names)
    n_on = len(tonsets)
    idx = [x for x in range(0, n_on)]
    step = int(n_on/n_types)
    numpy.random.shuffle(idx)

    for i, t in enumerate(type_names):
        si = i*step
        se = (i+1)*step
        if i == n_types:
            se = n_on
        with open('stims/example_00002_01_cue_cat'+t+'.1D', 'w') as f:
            f.write(" ".join(["%.02f" % x for x in tonsets[si:se]]))

    return((tonsets, sonsets))


def read_timing(onsetprefix):
    """
    read onsets files given a pattern. will append *1D to pattern
    #everything not in pattern is stripped from returned onset dict
    only file name is used
    use with parse_onsets()
       # input looks like
       with open('stims/example_0001_01_cue.1D','w') as f:
            f.write(" ".join(["%.02f:dur" % x
                      for x in numpy.cumsum(.5+numpy.repeat(2,10) ) ]));
       stims/4060499668621037816/
         dly.1D
         mgs.1D
         vgs_Left_Indoor.1D
         vgs_Left_None.1D
         vgs_Left_Outdoor.1D
         vgs_Right_Indoor.1D
         vgs_Right_None.1D
         vgs_Right_Outdoor.1D
    """
    onsetdict = {}
    onsetfiles = glob.glob(onsetprefix + '*1D')
    if(len(onsetfiles) <= 0):
        msg = 'no onset files in %s' % onsetprefix
        raise Exception(msg)
    for onset1D in onsetfiles:
        # key name will be file name but
        # remove the last 3 chars (.1D) and the glob part
        #onsettype = onset1D[:-3].replace(onsetprefix, '')
        onsettype = os.path.basename(onset1D)[:-3]
        with open(onset1D) as f:
            onsetdict[onsettype] = [float(x.split(':')[0])
                                    for x in f.read().split()]
    return(onsetdict)


def image_sets():
    allimages = glob.glob('img_circle/*png')
    # # break images into saccade images and novel (for memory quiz)
    novelfile = re.compile('.*\.01\..*')  # any .01. image
    sacc_images = [x for x in allimages if not novelfile.match(x)]
    novel_images = [x for x in allimages if novelfile.match(x)]
    return((sacc_images, novel_images))


def shuf_for_ntrials(vec,ntrials):
    '''
     shuf_for_ntrials creates a shuffled vector repeated to match the number of trials
    '''
    nitems = len(vec)
    if nitems == 0 or ntrials == 0:
        return([])

    items_over = ntrials % nitems
    nfullvec = int(math.floor(ntrials/nitems))
    # have 3 items want 5 trials
    # nfullvec=1; items_over=2

    # repeat full vector as many times as we can
    mat = numpy.matlib.repmat(vec, 1, nfullvec).flatten()
    # then add a truncated shuffled vector as needed
    if items_over > 0:
        numpy.random.shuffle(vec)
        mat = numpy.append(mat, vec[:items_over])

    numpy.random.shuffle(mat)
    return(mat)


def wait_until(stoptime, maxwait=30):
  """
  just like core.wait, but instead of waiting a duration
  we wait until a stoptime.
  optional maxwait will throw an error if we are wating too long 
  so we dont get stuck. defaults to 30 seconds
  """
  if stoptime - core.getTime()  > maxwait:
    raise ValueError("requiest to wait until stoptime is more than 30 seconds, secify maxwait to avoid this error")
  # will hog cpu -- no pyglet.media.dispatch_events here
  while core.getTime() < stoptime:
    continue
   
def response_should_be(pos,accept_keys):
    """
    evaluate known/unkown and left/right based on position and accept_keys
    position==nan means it was never seen
    neg. position is left, positive position is right
    """
    if(math.isnan(pos )): return( (accept_keys['unknown'],accept_keys['oops']) )
    elif( pos < 0): return( (accept_keys['known'],accept_keys['left']) ) 
    elif( pos > 0): return( (accept_keys['known'],accept_keys['left'])  )
    else: raise ValueError('bad pos?! how!?')
   
   
# we could  img.units='deg', but that might complicate testing on diff screens
def ratio(screen,image,scale): return(float(screen) * scale/float(image))
   
'''
 replace_img adjust the image and position of a psychopy.visual.ImageStim
'''
def replace_img(img,filename,horz,imgpercent=.04,defsize=(225,255)):

  # set image, get props
  if filename is not None:
      img.image=filename
      (iw,ih) = img._origSize
  else:
      (iw,ih) = defsize


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

  ## draw if we are not None
  if filename is not None:
      img.draw()

  return(img.pos)


def parse_onsets(onsetsprefix):
    """
    read in all files matching a glob
    return a by trial dataframe
    """
    onsets = read_timing(onsetsprefix)
    # first event is 'cue'. sort onsets dict by first onset time. pick first
    firstevent = sorted([ (k, min(v)) for k,v in onsets.items() ],key=lambda x: x[1] )[0][0] 
    if len(onsets) < 1:
        raise Exception("nothing to do! No onsets parsed from %s" % onsetsprefix)
    
    # make long format data frame
    d = pandas.DataFrame([[k, t] for k, v in onsets.items() for t in v])
    d.columns = ['event', 'onset']

    # set trial numbers
    d = d.sort_values('onset')
    d['trial'] = numpy.nan
    startrows = d.event.str.startswith(firstevent)
    tnums = [x + 1 for x in range(len(d[startrows]))]
    d.loc[startrows, 'trial'] = tnums

    # merge with info about vgs
    vgssplit = [[x] + x.split('_')[1:]
                for x in onsets.keys()
                if re.match('vgs', x)]

    if len(vgssplit) < 2:
        raise Exception("bad vgs onsets from %s" % onsetsprefix)

    # merge vgs array split with timing, name columns,
    # fill forward (so dly and mgs get side, image type, number)
    # remove all but first 3 chars of the event name
    df = pandas.DataFrame(vgssplit).\
         rename(columns={0: 'event', 1: 'side', 2: 'imgtype'}).\
         merge(d, how='outer').\
         sort_values(by='onset').\
         fillna(method='ffill').\
         assign(event=lambda x: [s[0:3] for s in x.event])

    # cue comes before vgs so is all messed up
    # the previous forwardfill fillna didn't do good things.
    # fix that with back fill
    df.loc[df.event=='cue',['side','imgtype']]=numpy.NaN
    df = df.fillna(method='bfill')

    # trial wide format
    trialdf = df.\
            set_index(['trial', 'event', 'side', 'imgtype']).\
            unstack('event').\
            reset_index()

    # reset columns
    trialdf.columns = [i[1] if i[0] == 'onset' else i[0]
                        for i in trialdf.columns]

    
    return(trialdf)


def gen_imagedf(path_dict):
    """
    find images and label to be merged with task 
    input is dict {'label: ['path/to/globimgs','path2'],..}
    - label matches vgs_ file names
    output is "imgtype","image" dataframe
    - imgtype names matches parse_onsets 
    """
    #path_dict={'Inside': ['SUN/circle_select/inside/*png'],
    #           'Outside': ['SUN/circle_select/outside_man/*png',
    #                       'SUN/circle_select/outside_nat/*png',
    #                      ]
    #           }
    # go through each label and the files that match all
    # patterns provided
    labeled_image_list = []
    for label, paths in path_dict.items():
        for p in paths:
            for img in glob.glob(p):
                labeled_image_list.append([label, img])

    df = pandas.DataFrame(labeled_image_list)
    df.columns = ['imgtype', 'imgfile']
    df['used'] = False
    return(df)


def gen(timingglob='stims/mri/135154167238784597/*'):
    """
    this is here for example usage. probably not called by anthing
    """
    path_dict = {'Indoor':  ['img/inside/*png'],
                 'Outdoor': ['img/outside_man/*png',
                             'img/outside_nat/*png',
                             ]}
    imagedf = gen_imagedf(path_dict)
    trialdf = parse_onsets(timingglob)
    (imagedf, trialdf) = gen_stimlist_df(imagedf, trialdf)


def pick_n_from_group(x, cnts):
    have_n = len(x)
    imgtype = x.imgtype.iloc[0]
    print('looking at %s' % imgtype)
    want_n = cnts.get(imgtype, 0)
    print('want %d' % want_n)
    take_n = min([want_n,have_n])
    return(x.sample(take_n))

    
def gen_stimlist_df(imagedf,trialdf):
    """
    given a trial df and an image df
    return "stimlist" array of dicts describing each trial
    """
    
    # dataframe gets a new colum for the image file
    trialdf['imgfile'] = None
    # go through each event type
    eventtypes = pandas.unique(sorted(trialdf.imgtype))
    for thisevent in eventtypes:
        searchstr = 'imgtype == "%s"' % thisevent
        idx = trialdf.query(searchstr).index
        needn = len(idx)
        if(needn <= 0):
            print("WARNING: need 0 trials of %s?! how is that possible?" % thisevent )
        img_aval = imagedf.query(searchstr + " & used == False")
        if len(img_aval) < needn:
            if thisevent == 'None':
                continue
            # TODO if len > 0 resample some
            print("WARNING: %s: not enough images (need %d > have %d)" % (thisevent,needn,len(img_aval)) )
        else: 
            trialdf.loc[idx,'imgfile'] = list(img_aval.sample(needn).imgfile)

    # set what we used in imagedf
    for f in pandas.unique(trialdf.imgfile):
        fileidx = imagedf.imgfile == f
        if any(fileidx):
            imagedf.loc[ fileidx ,'used'] = True
        else:
            if f is not None:
                print("WARNING: %s is not in imagedf! Where did it come from!?" % f)


    # set None to empty string
    #nofileidx = [x is None for x in trialdf.imgfile]
    #trialdf.loc[nofileidx,'imgfile'] = ''

    return(imagedf, trialdf)


def msg_screen(win, textbox, msg='no message given', pos=(0, 0)):
    textbox.pos = pos
    textbox.text = msg
    textbox.draw()
    win.flip()
    core.wait(.4)
    event.waitKeys()


class mgsTask:
    # initialize all the compoents we need
    def __init__(self,
                 win,
                 accept_keys={'known':   'k',
                              'unknown': 'd',
                              'left':    'd',
                              'right':   'k',
                              'oops':    'o'},
                 useArrington=False,
                 usePP=False):
        # settings for eyetracking and parallel port ttl (eeg)
        thisscript=os.path.abspath( os.path.dirname(__file__) )
        #self.vpxDll = os.path.join(thisscript,"VPX_InterApp.dll")
        self.vpxDll = 'C:\\Users\\Public\\Desktop\\tasks\\EyeTracking_ViewPointConnect\\VPX_InterApp.dll'
        self.useArrington = useArrington
        # # eyetracking
        if(self.useArrington):
            self.init_vpx()

        # settings for parallel port
        # see also 0x03BC, LPT2 0x0278 or 0x0378, LTP 0x0278
        self.pp_adress = 0x0378
        self.usePP = usePP

        self.verbose = True

        # images relative to screen size
        self.imgratsize = .15

        # window and keys
        self.win = win
        self.accept_keys = accept_keys

        # allocate screen parts 
        self.img = visual.ImageStim(win,name="imgdot") #,AutoDraw=False)
        self.crcl = visual.Circle(win,radius=10,lineColor=None,fillColor='yellow',name="circledot") #,AutoDraw=False)
        self.crcl.units = 'pix'

        self.timer = core.Clock()

        # could have just one and change the color
        self.iti_fix = visual.TextStim(win, text='+',name='iti_fixation',color='white')
        self.isi_fix = visual.TextStim(win, text='+',name='isi_fixation',color='yellow')
        self.cue_fix = visual.TextStim(win, text='+',name='cue_fixation',color='red')
        self.textbox = visual.TextStim(win, text='**',name='generic_textbox',alignHoriz='left',color='white',wrapWidth=2)

        # # for quiz
        self.text_KU = visual.TextStim(win, text='kown or unknown',name='KnownUnknown',color='white',pos=(0,-.75))
        self.text_LR = visual.TextStim(win, text='left or right',name='LeftRight',color='white',pos=(0,-.75))

        self.dir_key_text   = [(self.accept_keys['left'],   'left         '),
                                (self.accept_keys['right'],  '        right'),
                                (self.accept_keys['oops'],   '    oops     ')]
        self.known_key_text = [(self.accept_keys['known'],   'known           '),
                               (self.accept_keys['unknown'], '         unknown')]

    def eyetracking_newfile(self, fname):
        # start a new file and pause it
        if(self.useArrington):
            self.vpx.VPX_SendCommand('dataFile_NewName "%s"' % fname)
            self.vpx.VPX_SendCommand('dataFile_Pause 1')

    def eyetracking_start(self):
        if(self.useArrington):
            self.vpx.VPX_SendCommand('dataFile_Pause 0')

    def init_vpx(self):
        if not hasattr(self, 'vpx'):
            from ctypes import cdll, CDLL
            # vpxDll="C:/ARI/VP/VPX_InterApp.dll"
            if not os.path.exists(self.vpxDll):
                Exception('cannot find eyetracking dll @ ' + self.vpxDll)
            cdll.LoadLibrary(self.vpxDll)
            self.vpx = CDLL(self.vpxDll)
            if self.vpx.VPX_GetStatus(1) < 1:
                Exception('ViewPoint is not running!')
            self.vpx.VPX_SendCommand('say "mgs_task is connected"')

    def eventToTTL(event,side,catagory):
        if event == 'iti':
            return(255)
        # ttl codes are a composit of the event, and image side + catagory
        # allow unspecified triggers as 0
        # outside of 0, range is 61 (cue:None,Left) to 234 (mgs:Indoor,Right)
        # cues are all < 100 (61 -> 84); img < 150 (111 -> 134); isi < 200 ( 161 -> 184); mgs < 250 (211->234) 
        event_dict = {'bad': 0, 'cue': 50, 'img': 100, 'isi': 150, 'mgs': 200}
        ctgry_dict = {'bad': 0, 'None': 10, 'Outdoor': 20, 'Indoor': 30}
        side_dict = {'bad': 0, 'Left': 1, 'NearLeft': 2, 'NearRight': 3, 'Right': 4}
        composite = even_dict.get(event,0) + side_dict.get(side,0) + ctrgy_dict.get(catagory,0)
        return(composite)
        


    def init_PP(self):
        # TODO: TEST SOMEWHERE
        if(self.usePP):
            # initialize parallel port
            if not hasattr(self, 'port'):
                from psychopy import parallel
                self.port = parallel.ParallelPort(address=self.ppaddress)

    def log_and_code(self,event,side,catagory,logh=None,takeshots=None,num=1):
        self.send_code(event,side,catagory)
        if logh is not None:
            logh.log(level=logging.INFO, msg='flipped %s (%s,%s)' % (event, side, catagory))
        if takeshots:
            take_screenshot(self.win, takeshots + ('_%02d_%s' % (num, name) ))
            
        
    def send_code(self, event, side, catagory):
        """
        send a trigger on parallel port (eeg) or ethernet (eyetracker)
        in MR, we do eyetracking, and want to send a trigger to the tracker
        in EEG, we dont have eye tracking, but want to annotate screen flips
        """

        ttlstr = "_".join(map(lambda x: "%s" % x, [event,side,catagory]))
        # see also: vpx.VPX_GetStatus(VPX_STATUS_ViewPointIsRunning) < 1
        if self.useArrington:
            # initialze eyetracking
            self.vpx.VPX_SendCommand('dataFile_InsertString "%s"' % ttlstr)
            # TODO start with setTTL? see manual ViewPoint-UserGuide-082.pdf
        if self.usePP:
            # send code, or 100 if cannot find
            thistrigger = eventToTTL(event,side,catagory)
            self.port.setData(thistrigger)

        if self.verbose:
            print("sent code %s" % ttlstr)

    def wait_for_scanner(self, trigger):
        """
        wait for scanner trigger press
        return time of keypush
        """
        self.textbox.pos = (-1, 0)
        self.textbox.setText('Waiting for scanner (pulse trigger)' % trigger)
        self.textbox.draw()
        self.win.flip()
        event.waitKeys(keyList=trigger)
        starttime = core.getTime()
        self.eyetracking_start()
        self.run_iti()
        return(starttime)

    def run_iti(self, iti=0):
        """
        simple iti. flush logs
        globals:
          iti_fix visual.TextStim
        """
        self.iti_fix.draw()
        self.win.callOnFlip(self.log_and_code,'iti',None,None)
        showtime = self.win.flip()
        logging.flush()
        if(iti > 0):
            core.wait(iti)
        return(showtime)

    def vgs_show(self, imgon, posstr, imgfile=None, imgtype=None, logh=None, takeshots=False):
        """
        run the vgs event: show an image with a dot over it in some postiion
        """

        # set horz postion from side (left,right). center if unknown
        horz = {'Right': 1, 'Left': -1, 'NearLeft': -.5, 'NearRight': .5}.\
            get(posstr, 0)

        imgpos = replace_img(self.img, imgfile, horz, self.imgratsize)

        self.crcl.pos = imgpos
        self.crcl.draw()
        self.win.callOnFlip(self.log_and_code,'img',posstr,imgtype,logh,takeshots,num=2)
        wait_until(imgon)
        showtime = self.win.flip()
        return(showtime)

    def sacc_trial(self, t, starttime=0, takeshots=None, logh=None, tr=2):
        """
        saccade trial
         globals:
          win, cue_fix, isi_fix
        """
        if(starttime == 0):
            starttime = core.getTime()
        cueon = starttime + t['cue']
        imgon = starttime + t['vgs']
        ision = starttime + t['dly']
        mgson = starttime + t['mgs']
        mgsoff = mgson + tr
        imgfile = t['imgfile']

        # if takeshots: take_screenshot(self.win,takeshots+'_00_start')

        # print("")
        # print("ideal\tcur\tlaunch\tpos\ttype\tdly\tdiff (remaning iti)")
        print("%.02f\t%.02f\t%.02f\t%s\t%s\t%.02f\t%.02f" %
              (t['cue'],
               core.getTime(),
               starttime + t['cue'],
               t['side'],
               t['imgtype'],
               t['mgs'] - t['dly'],
               starttime + t['cue'] - core.getTime()
               ))

        # get ready red target
        self.cue_fix.draw()
        wait_until(cueon)
        self.log_and_code('cue', t['side'], t['imgtype'], logh, takeshots, 1)
        cueflipt = self.win.flip()

        # show an image if we have one to show
        vgsflipt = self.vgs_show(imgon, t['side'], t['imgfile'], t['imgtype'], logh, takeshots)

        # back to fix
        self.isi_fix.draw()
        wait_until(ision)
        self.win.callOnFlip(self.log_and_code, 'isi',t['side'], t['imgtype'], logh, takeshots, 3)
        isiflipt = self.win.flip()

        # memory guided (recall)
        # -- empty screen nothing to draw
        self.win.callOnFlip(self.log_and_code, 'mgs',t['side'], t['imgtype'], logh, takeshots, 4)
        wait_until(mgson)
        mgsflipt = self.win.flip()
        wait_until(mgsoff)

        # coded with wait instead of wait_until:
        # # get ready
        # cue_fix.draw(); win.flip(); core.wait(0.5)
        # # visual guided
        # replace_img(img,imgfile,horz,.05); win.flip(); core.wait(.5)
        # # back to fix
        # isi_fix.draw(); win.flip(); core.wait(0.5)
        # # memory guided
        # win.flip(); core.wait(.5)

    def key_feedback(self, keys_text_tupple, feedback, timer, maxtime=1.5):
        """
        record button response  and reaction time
        display equally long for regardless of RT
        provide feedback after push
        globals:
          win
        """
        validkeys = [x[0] for x in keys_text_tupple]
        origtext = feedback.text

        # get list of tuple (keypush,rt)
        t = event.waitKeys(keyList=validkeys, maxWait=maxtime, timeStamped=timer)
        # we're only going to look at single button pushes (already only accepting 2 or 3 keys)
        if(t is not None and len(t) == 1):
            (keypressed, rt) = t[0]
            for (k, txt) in keys_text_tupple:
                if(keypressed == k):  # TODO, allow multple keys?
                    feedback.text = txt
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

        self.textbox.pos = (-.9, 0)
        self.textbox.text = \
           'STEPS: Prep, Look, Wait, Recall, Relax\n\n' +\
           '1. Prep: Look at the red cross.\n' + \
           '\t An image is about to appear.\n\n' + \
           '2. Look: Look at the dot inside the image\n' + \
           '\t until it goes away.\n' + \
           '\t Remember where you looked.\n\n' + \
           '3. Wait: Look at the centered yellow cross.\n\n' + \
           '4. Recall: When the yellow cross goes away.\n' + \
           '\t Look where the image just was.\n\n' + \
           '5. Relax: Look center at the white cross.'
        # 'Color Hints: \n' + \
        # 'red = get ready\n' + \
        # 'yellow = remember\n' + \
        # 'white = relax'

        self.textbox.draw()
        self.instruction_flip()

        self.textbox.pos = (-.9,.9)
        self.textbox.text = 'Prep: get ready to look at an image'
        self.textbox.draw()
        self.cue_fix.draw()
        self.instruction_flip()

        self.textbox.text = 'Look: look at the dot on top of the image'
        imgpos = replace_img(self.img, 'img/example.png', 1, self.imgratsize)
        self.textbox.draw()
        self.crcl.pos = imgpos
        self.crcl.draw()
        self.instruction_flip()

        self.textbox.text = 'Wait: go back to center'
        self.textbox.draw()
        self.isi_fix.draw()
        self.instruction_flip()

        self.textbox.text = 'Recall: look to where image was'
        self.textbox.draw()
        self.instruction_flip()

        self.textbox.text = 'Relax: wait for the red cross to signal a new round'
        self.textbox.draw()
        self.iti_fix.draw()
        self.instruction_flip()
        self.textbox.pos = (0, 0)

    def run_end(self, run, nruns):
        self.textbox.pos = (-.2, 0)
        self.textbox.text = 'Finished %d/%d!' % (run, nruns)
        self.textbox.draw()
        self.instruction_flip()


def gen_run_info(nruns, datadir):
    """
    load or make and save
    timing for all blocks at once
    - useful to guaranty unique timing files and images
    - used images saved for recall
    """
    # where do we save this file?
    runs_info_file = os.path.join(datadir, 'runs_info.pkl')

    # if we have it, just return it
    if os.path.exists(runs_info_file):
        with open(runs_info_file, 'r') as f:
            return(pickle.load(f))

    # images
    path_dict = {'Indoor':  ['img/inside/*png'],
                 'Outdoor': ['img/outside_man/*png',
                             'img/outside_nat/*png',
                             ]}
    imagedf = gen_imagedf(path_dict)

    # get enough timing files for all runs
    alltimingdirs = glob.glob(os.path.join('stims', 'mri', '[0-9]*[0-9]'))
    thistimings = shuf_for_ntrials(alltimingdirs, nruns)
    # allocate array
    run_timing = []
    for runi in range(nruns):
        # find all timing files in this directory
        timingglob = os.path.join(thistimings[runi], '*')
        trialdf = parse_onsets(timingglob)
        # add images to trialdf, update imagedf with which are used
        (imagedf, trialdf) = gen_stimlist_df(imagedf, trialdf)
        # check
        if(any(numpy.diff(trialdf.vgs) < 0)):
            raise Exception('times are not monotonically increasing! bad timing!')
        run_timing.append(trialdf)

    # save to unified data structure
    subj_runs_info = {'imagedf': imagedf, 'run_timing': run_timing}

    # save what we have
    with open(runs_info_file, 'w') as f:
        pickle.dump(subj_runs_info, f)

    return(subj_runs_info)
