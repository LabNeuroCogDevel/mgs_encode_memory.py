# Memory Guided Saccade Encode and Recall

## Usage
1. install [psychopy](http://www.psychopy.org/)
2. run `mgs_enc_mem.py`

## The task

## Timing
`stimtime/00_mktime.bash` using [`genTaskTime`](https://github.com/LabNeuroCogDevel/genTaskTime) 

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

### image source 
Images are from [SUN](http://vision.princeton.edu/projects/2010/SUN) dataset. 
 * [all images](http://vision.princeton.edu/projects/2010/SUN/SUN397.tar.gz) (37Gb!, 38 uncompressed)
 * [3 level hierarchy annotation](http://vision.cs.princeton.edu/projects/2010/SUN/hierarchy_three_levels.zip) (<1Mb)

