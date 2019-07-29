# Memory Guided Saccade Encode and Recall

## Usage
1. install [psychopy](http://www.psychopy.org/)
2. run `mgs_enc_mem.py`
3. run `mgs_recall.py`

## Windows install
python -m pip --user install https://github.com/AndreMiras/pycaw/archive/master.zip

## The task

## Timing
`stimtime/00_mktime.bash` using [`genTaskTime`](https://github.com/LabNeuroCogDevel/genTaskTime) 

see also
`mgs_enc_mem.py` settings for each `tasktype` and confirm counts from genTaskTime greping cue for duration delimintor:
```
for f in stims/*/*/cue.1D; do echo -n " $(basename $(dirname $(dirname $f))) "; tr ' ' '\n' < $f | grep -c :; done|sort -u
```

number of runs:
`{'mri': 3, 'eeg': 4, 'practice': 1, 'behave': 2}`

number of trials per run:
`{mri: 24, eeg: 24, practice: 20 (@ faster pace), behave: 16}`

each run length in seconds:
`{'mri': 420, 'eeg': 358, 'practice': 65, 'behave': 240}`


## Eye tracking
Eye tracking interfaces with ViewPoint EyeTracker software (via Arrington Research and Avotec). see `MR_note.txt`

## TTL triggers
`inpout32.dll` should be in directory where python runs `from psychopy import parallel`

## Images
Selection made with `img_pick.py`:
```
# r,g,b all .1 from equal. percieved brightness around 1std of the mean
q = d.query('abs(r-.33) < .1 and abs(g-.33) < .1 and abs(b-.33) <.1 and abs(p-116) < 10 ')
```
after `imgedit.py` (help from `SUN/iminfo.py`) converted images into 225x225 circle pngs.

### More images
2017-12-07: identified 635 more browesing in alphebetical order
2018-11-27: removed some w/help from anna,`remove_c.bash` from [(list)](https://docs.google.com/spreadsheets/d/1U_CWaaSiaHqn59llR-xTQ-VhvngGJDUFqUBpA8H7d7w/edit?usp=sharing)

### image source 
Images are from [SUN](http://vision.princeton.edu/projects/2010/SUN) dataset. 
 * [all images](http://vision.princeton.edu/projects/2010/SUN/SUN397.tar.gz) (37Gb!, 38 uncompressed)
 * [3 level hierarchy annotation](http://vision.cs.princeton.edu/projects/2010/SUN/hierarchy_three_levels.zip) (<1Mb)

## Data analysis
are ttl triggers reporting resonable times? `eeg/read.py`
