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
import winmute
import socket


def host_tasktype():
    hosts = {'EEG': ['Oaco14Datapb1'],
             'MR': ['7T-EPRIME-PC'],
             'test': ['reese']}
    host = socket.gethostname()
    if host in hosts['EEG']:
        return('eeg')
    elif host in hosts['MR']:
        return('mri')
    elif host in hosts['test']:
        return('test')
    else:
        print("dont know about host '%s', task type is unknown" % host)
        return('unknown')


def getSubjectDataPath(subjid, tasktype, imgset, timepoint):
    """
    generate (and create) a path to save subjects visit data
    directory for subject and task like "10931/01_eeg_A"
    """
    savepath = 'subj_info'
    taskinfo = "%02d_%s_%s" % (timepoint, tasktype, imgset)
    datadir = os.path.join(savepath, subjid, taskinfo)
    logdir = os.path.join(datadir, 'log')
    for thisoutdir in [savepath, datadir, logdir]:
        if not os.path.exists(thisoutdir):
            os.makedirs(thisoutdir)

    return((datadir, logdir))


def getInfoFromDataPath(datadir):
    """
    get subject info from path
    expects os.dirname(pkl_file)
    from subj_info/someid/01_eeg_A
    to ("someid", "eeg", "A", 1 )
    """
    print(datadir)
    # match to subj_info directory with
    # dir delimiter like linux (/) or windows (\, escaped as \\\)
    rm_str = ".*subj_info[/\\\\]"
    print(rm_str)
    justdir = re.sub(rm_str, "", datadir)
    (subjid, taskinfo) = os.path.split(justdir)
    (timepoint, imgset, tasktype) = taskinfo.split("_")
    timepoint = int(timepoint)
    return((subjid, tasktype, imgset, timepoint))


# this causes some artifacts!?
def take_screenshot(win, name):
    if not os.path.exists('screenshots/'):
        os.mkdir('screenshots')
    win.getMovieFrame()   # Defaults to front buffer, I.e. what's on screen now
    win.saveMovieFrames('screenshots/' + name + '.png')


def eventToTTL(event, side, catagory):
    """
    make trigger from event, side, and catagory
    event inc in 50: (50-200: cue,img,isi,mgs)
    catagory inc in 10 (10->30: None,Outdoor,Indoor)
    side inc in 1 (1->4: Left -> Right)
    61 == cue:None,Left
    234 == mgs:Indoor,Right

    iti,start,end hardcoded => 245,128,129
    """
    if event == 'iti':
        return(254)
    if event == 'start':
        return(128)
    if event == 'end':
        return(129)
    # ttl codes are a composit of the event, and image side + catagory
    # allow unspecified triggers as 0
    # outside of 0, range is 61 (cue:None,Left) to 234 (mgs:Indoor,Right)
    # cues  < 100 (61 -> 84); img < 150 (111 -> 134);
    # isi < 200 ( 161 -> 184); mgs < 250 (211->234)
    event_dict = {'bad': 0, 'cue': 50, 'img': 100, 'isi': 150, 'mgs': 200}
    ctgry_dict = {'bad': 0, 'None': 10, 'Outdoor': 20, 'Indoor': 30}
    side_dict = {'bad': 0, 'Left': 1,
                 'NearLeft': 2, 'NearRight': 3, 'Right': 4}
    composite = event_dict.get(event, 0) + \
                side_dict.get(side, 0) + \
                ctgry_dict.get(catagory, 0)
    return(composite)


def center_textbox(textbox):
    """
    center textbox in 'norm' units
    """
    tw = textbox.boundingBox[0]
    ww = float(textbox.win.size[0])
    textbox.pos = (-tw/ww, 0)


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
        # onsettype = onset1D[:-3].replace(onsetprefix, '')
        onsettype = os.path.basename(onset1D)[:-3]
        with open(onset1D) as f:
            onsetdict[onsettype] = [float(x.split(':')[0])
                                    for x in f.read().split()]
    return(onsetdict)


def shuf_for_ntrials(vec, ntrials):
    '''
     shuf_for_ntrials creates a shuffled vector
     repeated to match the number of trials
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
    if stoptime - core.getTime() > maxwait:
        raise ValueError("request to wait until stoptime is more than " +
                         "30 seconds, secify maxwait to avoid this error")
    # will hog cpu -- no pyglet.media.dispatch_events here
    while core.getTime() < stoptime:
        continue


def response_should_be(pos, accept_keys):
    """
    evaluate known/unknown and left/right based on position and accept_keys
    position==nan means it was never seen
    neg. position is left, positive position is right
    """

    # are we "near" left or right
    if(pos != round(pos, 0)):
        near_str = 'Near'
    else:
        near_str = ''

    if(math.isnan(pos)):
        return((accept_keys['unknown'], accept_keys['oops']))
    elif(pos < 0):
        return((accept_keys['known'], accept_keys[near_str + 'Left']))
    elif(pos > 0):
        return((accept_keys['known'], accept_keys[near_str + 'Right']))
    else:
        raise ValueError('bad pos?! how!?')


# we could  img.units='deg', but that might complicate testing on diff screens
def ratio(screen, image, scale):
    return(float(screen) * scale/float(image))


def replace_img(img, filename, horz, imgpercent=.04, defsize=(225, 255)):
    '''
    replace_img adjust the image and position of a psychopy.visual.ImageStim
    '''
    # set image, get props
    if filename is not None:
        img.image = filename
        (iw, ih) = img._origSize
    else:
        (iw, ih) = defsize

    (sw, sh) = img.win.size
    img.units = 'pixels'

    # resize img
    scalew = ratio(sw, iw, imgpercent)
    # scaleh= ratio(sh,ih,imgpercent)
    # scale evenly in relation to x-axis
    # img.size=(scalew*iw,scalew*sw/sh*ih) # if units were 'norm'
    img.size = (scalew*iw, scalew*ih)  # square pixels
    # img._requestedSize => (80,80) if imgprecent=.1*sw=800

    # # position
    winmax = sw/float(2)
    # horz=-1 => -400 for 800 wide screen
    horzpos = horz*winmax
    halfimgsize = scalew*iw/2.0
    # are we partially off the screen? max edges perfect
    if horzpos - halfimgsize < -winmax:
        horzpos = halfimgsize - winmax
    elif horzpos + halfimgsize > winmax:
        horzpos = winmax - halfimgsize
    # set
    img.pos = (horzpos, 0)

    # # draw if we are not None
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
    firstevent = sorted([(k, min(v)) for k, v in onsets.items()],
                        key=lambda x: x[1])[0][0]
    if len(onsets) < 1:
        raise Exception("nothing to do! No onsets parsed from %s" %
                        onsetsprefix)

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
    df.loc[df.event == 'cue', ['side', 'imgtype']] = numpy.NaN
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
    # path_dict={'Inside': ['SUN/circle_select/inside/*png'],
    #            'Outside': ['SUN/circle_select/outside_man/*png',
    #                        'SUN/circle_select/outside_nat/*png',
    #                       ]
    #            }
    # go through each label and the files that match all
    # patterns provided
    labeled_image_list = []
    for label, paths in path_dict.items():
        for p in paths:
            subdir = os.path.basename(os.path.dirname(p))
            for img in glob.glob(p):
                labeled_image_list.append([label, img, subdir])

    print(path_dict.items())
    df = pandas.DataFrame(labeled_image_list)
    df.columns = ['imgtype', 'imgfile', 'subtype']
    df['used'] = False
    return(df)


def gen(imgset='A', timingglob='stims/mri/135154167238784597/*'):
    """
    this is here for example usage. probably not called by anthing
    """
    path_dict = {'Indoor':  ['img/' + imgset + '/inside/*png'],
                 'Outdoor': ['img/' + imgset + '/outside_man/*png',
                             'img/' + imgset + '/outside_nat/*png',
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
    take_n = min([want_n, have_n])
    return(x.sample(take_n))


def dist_total_into_n(total, n):
    """
    @param: total - total to be distrubuted
    @param: n - number of elements
    @return: n length array that sums to total
    """
    if n == 0 or total == 0:
        return([])
    arr = [float(total)/float(n)]*n
    arr[0] = int(numpy.ceil(arr[0]))
    arr[1:] = [int(numpy.floor(x)) for x in arr[1:]]
    if numpy.sum(arr) != total:
        raise ValueError('total %d not matched in %s' % (total, arr))
    numpy.random.shuffle(arr)
    return(arr)


def gen_stimlist_df(imagedf, trialdf):
    """
    given a trial df and an image df
    return "stimlist" array of dicts describing each trial
    N.B. operations on imagedf are inplace as well as returned!
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
            print("WARNING: need 0 trials of %s?! how is that possible?" %
                  thisevent)
        img_aval = imagedf.query(searchstr + " & used == False")
        if len(img_aval) < needn:
            if thisevent == 'None':
                continue
            # TODO if len > 0 resample some
            print("WARNING: %s: not enough images (need %d > have %d)" %
                  (searchstr, needn, len(img_aval)))
        else:
            # within the trial type there maybe a subtype (outside_man, outside_nat)
            subtypes = pandas.unique(img_aval.subtype)
            if len(subtypes) <= 1:
                # this condition is not needed. below would work fine for even n=1
                # left for clarity
                this_samp = img_aval.sample(needn)
                trialdf.loc[idx, 'imgfile'] = this_samp.imgfile.values
                # print('%s: setting %d to used' % (subtypes[0], len(this_samp.index)))
                imagedf.loc[this_samp.index, 'used'] = True
            else:
                # if we have 10 trials and 2 types
                # needns will be [5, 5]
                needns = dist_total_into_n(needn, len(subtypes))
                # shuffle the index of trial df that need this imagetype
                # so we can assing images to random trials (within imagetype)
                idx_shuf = list(idx)
                numpy.random.shuffle(idx_shuf)
                starti = 0
                # print('dist subtypes: %s for %s' % (needns,subtypes))
                for i in range(len(subtypes)):
                    # use index to get values
                    # starti-endi is what indexes to pull from trialdf idx
                    thissubtype = subtypes[i]
                    num = needns[i]
                    endi = starti+num
                    # narrow what images we take
                    img_aval = imagedf.query(searchstr + " & subtype == @thissubtype & used == False")
                    intoidx = idx_shuf[starti:endi]
                    # what if we dont have enough images!?
                    if len(img_aval) < num:
                        print("WARNING: %s+%s: not enough images (need %d > have %d)"
                              % (thisevent, thissubtype, needn, len(img_aval)))
                    # sample the avaible images, mark as used
                    this_samp = img_aval.sample(num)
                    usethese = this_samp.imgfile.values
                    trialdf.loc[intoidx, 'imgfile'] = usethese
                    imagedf.loc[this_samp.index, 'used'] = True
                    # update the new starti for trialdf idx
                    starti = endi
    return(imagedf, trialdf)


def msg_screen(win, textbox, msg='no message given', pos=(0, 0)):
    textbox.pos = pos
    textbox.text = msg
    textbox.draw()
    win.flip()
    core.wait(.4)
    event.waitKeys()


def create_window(fullscr):
    """ create window either fullscreen or 800,600
    hide mouse cursor and make active
    """
    # setup screen
    if fullscr:
        win = visual.Window(fullscr=fullscr)
    else:
        win = visual.Window([800, 600])

    win.winHandle.activate()  # make sure the display window has focus
    win.mouseVisible = False  # and that we don't see the mouse
    return(win)


class mgsTask:
    # initialize all the compoents we need
    def __init__(self,
                 win,
                 accept_keys={'known':        '1',
                              'maybeknown':   '2',
                              'maybeunknown': '9',
                              'unknown':      '0',
                              'Left':         '1',
                              'NearLeft':     '2',
                              'NearRight':    '9',
                              'Right':        '9',
                              'oops':         '5'},
                 useArrington=False,
                 usePP=False,
                 fullscreen=True):
        # were we given a window?
        # make our own if not
        if win is None:
            win = create_window(fullscreen)

        # settings for eyetracking and parallel port ttl (eeg)
        # thisscript=os.path.abspath(os.path.dirname(__file__))
        # self.vpxDll = os.path.join(thisscript,"VPX_InterApp.dll")
        self.vpxDll = 'C:\\Users\\Public\\Desktop\\tasks\\EyeTracking_ViewPointConnect\\VPX_InterApp.dll'
        self.useArrington = useArrington
        # # eyetracking
        if(self.useArrington):
            self.init_vpx()

        # settings for parallel port
        # see also 0x03BC, LPT2 0x0278 or 0x0378, LTP 0x0278
        #self.pp_address = 0x0378
        #self.pp_address = 0x0278
        self.pp_address = 0xDFF8

        self.usePP = usePP
        if usePP:
            self.init_PP()

        # want to mute windows computer
        # so monitor switching doesn't beep
        self.winvolume = winmute.winmute()

        self.verbose = True

        # images relative to screen size
        self.imgratsize = .15

        # window and keys
        self.win = win
        self.accept_keys = accept_keys

        # allocate screen parts
        self.img = visual.ImageStim(win, name="imgdot")
        self.crcl = visual.Circle(win, radius=10, lineColor=None,
                                  fillColor='yellow', name="circledot")
        #  ,AutoDraw=False)
        self.crcl.units = 'pix'

        # instruction eyes image
        # for draw_instruction_eyes(self,
        self.eyeimg = visual.ImageStim(win, name="eye_img_instructions")
        self.eyeimg.image = 'img/instruction/eyes_center.png'
        self.eyeimg.pos = (0, -.9)

        self.timer = core.Clock()

        # could have just one and change the color
        self.iti_fix = visual.TextStim(win, text='+', name='iti_fixation', color='white')
        self.isi_fix = visual.TextStim(win, text='+', name='isi_fixation', color='yellow')
        self.cue_fix = visual.TextStim(win, text='+', name='cue_fixation', color='lightblue')
        self.textbox = visual.TextStim(win, text='**', name='generic_textbox',
                                       alignHoriz='left', color='white',
                                       wrapWidth=2)

        # # for quiz
        self.text_KU = visual.TextStim(win,
                                       text='seen:\nyes, maybe yes | maybe no, no',
                                       name='KnownUnknown',
                                       alignHoriz='center',
                                       color='white',
                                       height=.07,
                                       wrapWidth=2,
                                       pos=(-0.2, -.75))
        # self.text_KU.units = 'pixels'
        # self.text_KU.size = 8
        self.text_LR = visual.TextStim(win,
                                       text='side:\nfar left, mid left | mid right, far right',
                                       name='LeftRight',
                                       alignHoriz='center',
                                       color='white',
                                       height=0.07,
                                       wrapWidth=2,
                                       pos=(-0.2, -.75))
        # self.text_LR.units = 'pixels'
        # self.text_LR.size = 8

        # for recall only:
        # tuplet of keys and text: like ('1', 'text after pushed')
        self.dir_key_text = [
                             (self.accept_keys['Left'],   'left'),
                             (self.accept_keys['NearLeft'],  '   left'),
                             (self.accept_keys['NearRight'],  'right    '),
                             (self.accept_keys['Right'],  '        right'),
                             (self.accept_keys['oops'],   '    oops     ')
                             ]
        self.known_key_text = [
                               (self.accept_keys['known'], 'known'),
                               (self.accept_keys['maybeknown'], 'known'),
                               (self.accept_keys['maybeunknown'], 'unkown'),
                               (self.accept_keys['unknown'], 'unknown')
                               ]

        # show side
        self.recall_sides = [visual.Circle(win, radius=10, lineColor=None,
                                           fillColor='yellow',
                                           units='pix',
                                           name="recall_dot%d" % x)
                             for x in range(4)]
        self.recall_txt = [visual.TextStim(win, text=str(x),
                                           color='black',
                                           units='pix',
                                           name='recall_%d' % x)
                           for x in range(4)]

    def eyetracking_newfile(self, fname):
        # start a new file and pause it
        if(self.useArrington):
            fname = str(fname)
            self.vpx.VPX_SendCommand('dataFile_Pause 1')
            self.vpx.VPX_SendCommand('dataFile_NewName "%s"' % fname)
            if self.verbose:
                print("tried to open eyetracking file %s" % fname)
                self.vpx.VPX_SendCommand('say "newfile %s"' % fname)

    def start_aux(self):
        """
        start eyetracking, send start ttl to parallel port
        """
        self.winvolume.mute_all()
        if(self.useArrington):
            self.vpx.VPX_SendCommand('dataFile_Pause 0')
        if(self.usePP):
            self.send_code('start', None, None)

    def stop_aux(self):
        """
        stop eyetracking file, send start ttl to parallel port
        """
        if(self.useArrington):
            self.vpx.VPX_SendCommand('dataFile_Close 0')
        if(self.usePP):
            self.send_code('end', None, None)
        #self.winvolume.undo_mute() #  causes error
        self.winvolume.unmute_all()

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

    def init_PP(self):
        # TODO: TEST SOMEWHERE
        if(self.usePP):
            # initialize parallel port
            if not hasattr(self, 'port'):
                from psychopy import parallel
                self.port = parallel.ParallelPort(address=self.pp_address)

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

        # see also: vpx.VPX_GetStatus(VPX_STATUS_ViewPointIsRunning) < 1
        if self.useArrington:
            ttlstr = "_".join(map(lambda x: "%s" % x, [event,side,catagory]))
            self.vpx.VPX_SendCommand('dataFile_InsertString "%s"' % ttlstr)
            if self.verbose:
                print("eye code %s" % ttlstr)
                self.vpx.VPX_SendCommand('say "sent %s"'% ttlstr)
            # TODO start with setTTL? see manual ViewPoint-UserGuide-082.pdf
        if self.usePP:
            # send code, or 100 if cannot find
            thistrigger = eventToTTL(event, side, catagory)
            self.send_ttl(thistrigger)


    def send_ttl(self, thistrigger):
        """
        send ttl trigger to parallel port (setup by init_PP)
        wait 10ms and send 0
        """
        thistrigger = int(thistrigger)
        self.port.setData(thistrigger)
        if self.verbose:
            print("eeg code %s" % thistrigger)
        core.wait(.01)  # wait 10ms and send zero
        self.port.setData(0)

    def wait_for_scanner(self, trigger, msg='Waiting for scanner (pulse trigger)'):
        """
        wait for scanner trigger press
        start any auxilary things (eyetracking for mri, ttl for eeg)
        return time of keypush
        """
        self.textbox.setText(msg % trigger)
        center_textbox(self.textbox)
        self.textbox.draw()
        self.win.flip()
        event.waitKeys(keyList=trigger)
        starttime = core.getTime()
        self.start_aux()  # eyetracking/parallel port
        self.run_iti()
        return(starttime)

    def run_iti(self, iti=0):
        """
        simple iti. flush logs
        globals:
          iti_fix visual.TextStim
        """
        self.iti_fix.draw()
        self.win.callOnFlip(self.log_and_code, 'iti', None, None)
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
        self.win.callOnFlip(self.log_and_code, 'img', posstr, imgtype,
                            logh, takeshots, num=2)
        wait_until(imgon)
        showtime = self.win.flip()
        return(showtime)

    def sacc_trial(self, t, starttime=0, takeshots=None, logh=None):
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

        # if takeshots: take_screenshot(self.win,takeshots+'_00_start')

        # give header for output if this is the first trial
        if t.thisN == 0:
            print("")
            print("ideal\tcur\tlaunch\tpos\ttype\tdly\tdiff (remaning iti)")

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
        self.win.callOnFlip(self.log_and_code, 'cue', t['side'], t['imgtype'],
                            logh, takeshots, 1)

        wait_until(cueon)
        cueflipt = self.win.flip()

        # show an image if we have one to show
        vgsflipt = self.vgs_show(imgon, t['side'], t['imgfile'], t['imgtype'],
                                 logh, takeshots)

        # back to fix
        self.isi_fix.draw()
        self.win.callOnFlip(self.log_and_code, 'isi', t['side'], t['imgtype'],
                            logh, takeshots, 3)

        wait_until(ision)
        isiflipt = self.win.flip()

        # memory guided (recall)
        # -- empty screen nothing to draw
        self.win.callOnFlip(self.log_and_code, 'mgs', t['side'], t['imgtype'],
                            logh, takeshots, 4)
        wait_until(mgson)
        mgsflipt = self.win.flip()

        # ----
        # N.B. after this filp we still need to wait MGS wait time
        # ---

        # send back all the flip times
        return({'cue': cueflipt, 'vgs': vgsflipt, 'dly': isiflipt,
                'mgs': mgsflipt})

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
        # validkeys = ['1','2','3','4']
        origtext = feedback.text

        # get list of tuple (keypush,rt)
        t = event.waitKeys(keyList=validkeys, maxWait=maxtime,
                           timeStamped=timer)
        # we're only going to look at single button pushes
        # already only accepting 2 or 3 keys
        if(t is not None and len(t) == 1):
            (keypressed, rt) = t[0]
            for (k, txt) in keys_text_tupple:
                if(keypressed == k):  # TODO, allow multple keys?
                    feedback.text = txt
                    break

            feedback.draw()
            self.win.flip()
            feedback.text = origtext
        # no response or too many responses means no keypress and no rt
        else:
            t = [(None, None)]
        # wait to finish
        while(maxtime != numpy.Inf and timer.getTime() < maxtime):
            pass
        # give key and rt
        return(t[0])

    def recall_instructions(self):
        """
        recall task instructions
        """

        self.textbox.pos = (-.9, 0)
        self.textbox.text = \
           'STEPS:\n\n' + \
           '1. push %s if you already saw the image.\n' % self.accept_keys['known'] + \
           '   push %s if you saw the image, but are uncertian\n' % self.accept_keys['maybeknown'] + \
           '   push %s if the image is new, but are uncertian\n' % self.accept_keys['maybeunknown'] + \
           '   push %s if the image is new\n\n' % self.accept_keys['unknown'] + \
           '2. If you have seen the image:\n' + \
           '   push %s if you saw it on the far left\n' % self.accept_keys['Left'] + \
           '   push %s if you saw it on the near left\n' % self.accept_keys['NearLeft'] + \
           '   push %s if you saw it on the near right\n' % self.accept_keys['NearRight'] + \
           '   push %s if you saw it on the far right\n' % self.accept_keys['Right'] 
           
        # '   push %s if you did not actually see it\n\n' % self.accept_keys['oops'] + \
        self.textbox.draw()
        self.instruction_flip()

    def init_recall_side(self):
        pos = [-1, -.5, .5, 1]
        keys = [self.accept_keys[x]
                for x in ['Left', 'NearLeft', 'NearRight', 'Right']]
        for i in range(len(pos)):
            self.recall_sides[i].pos = \
                    replace_img(self.img, None, pos[i], self.imgratsize)
            self.recall_txt[i].pos = self.recall_sides[i].pos
            self.recall_txt[i].text = str(keys[i])

    def recall_trial(self, imgfile, rspmax=numpy.Inf):
        """
        run a recall trial.
        globals:
         img, text_KU, text_LR, dir_key_text, known_key_text
        """
        # draw the image and the text (keep image on across flips)
        replace_img(self.img, imgfile, 0, .25)
        self.img.setAutoDraw(True)
        self.text_KU.draw()
        self.win.flip()

        self.timer.reset()
        # do we know this image?
        (knowkey, knowrt) = self.key_feedback(self.known_key_text,
                                              self.text_KU, self.timer,
                                              rspmax)

        # end early if we have not seen this before
        knownkeys = [self.accept_keys['maybeknown'], self.accept_keys['known']]
        if(knowkey not in knownkeys):
            self.img.setAutoDraw(False)
            # TODO: maybe wait so we are not incentivising unknown
            return((knowkey, None), (knowrt, None))

        # we think we remember this image, do we remember where it was
        self.text_LR.draw()
        for i in range(4):
            self.recall_sides[i].draw()
            self.recall_txt[i].draw()
        self.win.flip()

        self.timer.reset()
        (dirkey, dirrt) = self.key_feedback(self.dir_key_text,
                                            self.text_LR, self.timer,
                                            rspmax)

        self.img.setAutoDraw(False)
        return((knowkey, dirkey), (knowrt, dirrt))

    def instruction_flip(self):
        """
        quick def to flip, stall half a second, and wait for any key
        """
        self.win.flip()
        core.wait(.4)
        event.waitKeys()

    def draw_instruction_eyes(self, where='center'):
        self.eyeimg.image = 'img/instruction/eyes_%s.png' % where
        self.eyeimg.draw()


    def sacc_instructions(self):
        """
        saccade task instructions
        """
        self.textbox.pos = (-.5, 0)
        self.textbox.text = 'MGS Encode Task\n\nReady for a walk through?'
        self.textbox.draw()
        self.instruction_flip()

        self.textbox.pos = (-.9, .9)
        self.textbox.text = 'Prep: get ready to look at an image'
        self.textbox.draw()
        self.cue_fix.draw()
        self.draw_instruction_eyes('center')
        self.instruction_flip()

        self.textbox.text = \
            'Look: look at the dot on top of the image until ...\n'
        imgpos = replace_img(self.img, 'img/example.png', 1, self.imgratsize)
        self.textbox.draw()
        self.crcl.pos = imgpos
        self.crcl.draw()
        self.draw_instruction_eyes('right')
        self.instruction_flip()

        self.textbox.text = 'Wait: go back to center and focus there until ...'
        self.textbox.draw()
        self.isi_fix.draw()
        self.draw_instruction_eyes('center')
        self.instruction_flip()

        self.textbox.text = 'Recall: look to where image was and focus there until ...'
        self.textbox.draw()
        self.draw_instruction_eyes('right')
        self.instruction_flip()

        self.textbox.text = 'Relax: wait for the red cross to signal a new round'
        self.textbox.draw()
        self.iti_fix.draw()
        self.draw_instruction_eyes('center')
        self.instruction_flip()

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
            '5. Relax: Look center at the white cross.\n\n' +\
            'NOTE: you do not need to remember the images for this task\n' +\
            'but you may be asked about them later'
        # 'Color Hints: \n' + \
        # 'red = get ready\n' + \
        # 'yellow = remember\n' + \
        # 'white = relax'

        self.textbox.draw()
        self.instruction_flip()
        self.textbox.pos = (0, 0)

    def run_end(self, run=1, nruns=1):
        """
        show end of run screen
        send stop codes for parallel port
        close eyetracking file
        """
        self.stop_aux()  # end ttl, close eye file
        self.textbox.pos = (-.2, 0)
        runstr = ""
        if nruns > 1:
            runstr = '%d/%d!' % (run, nruns)
        self.textbox.text = 'Finished ' + runstr
        self.textbox.draw()
        self.instruction_flip()


def gen_run_info(nruns, datadir, imgset, task='mri'):
    """
    load or make and save
    timing for all blocks at once
    - useful to guaranty unique timing files and images
    - used images saved for recall
    task is mri or eeg
    """
    # where do we save this file?
    runs_info_file = os.path.join(datadir, 'runs_info.pkl')

    # if we have it, just return it
    if os.path.exists(runs_info_file):
        print('reusing timing/image selection from %s' % runs_info_file)
        with open(runs_info_file, 'rU') as f:
            return(pickle.load(f))

    # images
    path_dict = {'Indoor':  ['img/' + imgset + '/inside/*png'],
                 'Outdoor': ['img/' + imgset + '/outside_man/*png',
                             'img/' + imgset + '/outside_nat/*png',
                             ]}
    imagedf = gen_imagedf(path_dict)

    # get enough timing files for all runs
    alltimingdirs = glob.glob(os.path.join('stims', task, '[0-9]*[0-9]'))
    print("loading task timing for %s: %s" % (task, alltimingdirs))

    thistimings = shuf_for_ntrials(alltimingdirs, nruns)
    # allocate array
    run_timing = []
    for runi in range(nruns):
        # find all timing files in this directory
        timingglob = os.path.join(thistimings[runi], '*')
        trialdf = parse_onsets(timingglob)
        # add images to trialdf, update imagedf with which are used
        (imagedf, trialdf) = gen_stimlist_df(imagedf, trialdf)
        #print("nused = %d for %d" % (imagedf[imagedf.used].shape[0], trialdf.shape[0]))
        # check
        if(any(numpy.diff(trialdf.vgs) < 0)):
            raise Exception('times are not monotonically increasing! bad timing!')
        run_timing.append(trialdf)

    # save to unified data structure
    subj_runs_info = {'imagedf': imagedf, 'run_timing': run_timing}

    # save what we have
    with open(runs_info_file, 'wb') as f:
        pickle.dump(subj_runs_info, f)

    return(subj_runs_info)


def imagedf_to_novel(imdf):
    """
    take an imagedf with imgtype,subtype and used column
    return shuffled df with just the unused images matched on number of used
    """
    nused = imdf[imdf.used].\
            groupby(['imgtype','subtype']).\
            aggregate({'used': lambda x: x.shape[0]})
    nused['aval'] = imdf[~imdf.used].\
            groupby(['imgtype','subtype'])['used'].\
            apply(lambda x: x.shape[0])
    print(nused)
    if(any(nused.used > nused.aval)):
        print("WARNING: will see more repeats than novel images!")
    
    # use as many as we can
    # might not be balanced!
    novelimg = pandas.concat([
        imdf[(imdf.used == False) &
             (imdf.imgtype == r[0][0]) &
             (imdf.subtype == r[0][1]) ].
        sample(min(r[1].aval,r[1].used))
        for r in nused.iterrows()])
    # add empty position
    novelimg['pos'] = float("nan")
    return(novelimg)


def recallFromPickle(pckl, lastrunidx=3):
    """
    use a pckl file to define a trial list for recall
    """
    # load run info
    with open(pckl, 'rU') as p:
        print(pckl)
        run_data = pickle.load(p)

    # select what we've seen
    # put all runs together
    seendf = pandas.concat(run_data['run_timing'][0:lastrunidx])
    # --- pick some novel stims --
    imdf = run_data['imagedf']
    # but remove images we haven't seen (but should have)
    if(lastrunidx < len(run_data['run_timing'])):
        actuallysaw = pandas.unique(seendf['imgfile'])
        unsee = [x not in actuallysaw for x in imdf['imgfile']]
        imdf.loc[unsee, 'used'] = False

    # from that, make a novelimg dataset
    # with columns that match
    novelimg = imagedf_to_novel(imdf)

    # get just the images and their side
    seendf = seendf[seendf.imgtype != "None"][['side', 'imgfile', 'imgtype']]
    # convert side to position (-1 '*Left', 1 if '*Right')
    seendf['pos'] = [
            ('Left' == x) * -1 + ('Right' == x) * 1 +
            ('NearLeft' == x) * -.5 + ('NearRight' == x) * .5
            for x in seendf['side']]

    # combine them
    trialdf = pandas.concat([seendf[['imgfile', 'pos', 'imgtype']],
                         novelimg[['imgfile', 'pos', 'imgtype']]]).\
                         sample(frac = 1, replace = False)

    # set(trialdf.imgfile[pandas.notnull(df.pos)]) == \
    # set(seendf.imgfile[pandas.notnull(seendf.imgfile)])
    return(trialdf)
