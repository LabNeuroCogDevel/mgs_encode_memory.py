# Memory Guided Saccade Encode and Recall

Initially a single psychopy saccade and recall paradigm, now this repo contains a small suit of saccade tasks.

## Usage
1. install [psychopy](http://www.psychopy.org/)
2. run `mgs_enc_mem.py`
3. run `mgs_recall.py`

### Windows install
additionally a library to toggle volume so monitor re/connect notifications are not audible: 

```
python -m pip --user install https://github.com/AndreMiras/pycaw/archive/master.zip
```


## Additional Tasks
 - `vgs_anti.py`   - eeg anti or vgs (not mixed)
 - `ring_reward.py`- behavioral "rewarded" antisaccade task
 - `eeg_eyecal.py`- eeg eog eye position calibration task

## MGS Timing
[`stimtime/00_mktime.bash`](https://github.com/LabNeuroCogDevel/mgs_encode_memory.py/blob/master/stimtime/00_mktime.bash#L22) uses [`genTaskTime`](https://github.com/LabNeuroCogDevel/genTaskTime) to generate distribution and duration of events. 
  * Cue, VGS, and MGS each have a `2s` duration
  * Dly 15 @ 6.00s, 7 @ 8.00s, 2 @ 10.00s
  * ITI varies by modality.

Modality settings are also, redundantly, set in [`mgs_enc_mem.py`](https://github.com/LabNeuroCogDevel/mgs_encode_memory.py/blob/master/mgs_enc_mem.py#L21)
  * number of runs: `{'mri': 3, 'eeg': 4, 'practice': 1, 'behave': 2}`
  * number of trials per run: `{mri: 24, eeg: 24, practice: 20 (@ faster pace), behave: 16}`
  * each run length in seconds: `{'mri': 420, 'eeg': 358, 'practice': 65, 'behave': 240}`


For a quick check, compare the `mktime` outputs:
```
for f in stims/*/*/cue.1D; do task=$(basename $(dirname $(dirname $f))); tr ' ' '\n' < $f|sed 's/.*://;/^$/d'|sort |uniq -c|sed s/^/$task/; done|sort -u|column -t
```
```
MODALITY   NTRIAL CUEDUR
behave     16     2.00
eeg        24     2.00
mri        24     2.00
practice   20     1.00
```

## Eye tracking
 * Eye tracking interfaces with ViewPoint EyeTracker software (via Arrington Research and Avotec). see `MR_note.txt`
 * EEG eye tracking using EOG after collecting calibration with `eeg_eyecal.py`
 * ASL eye tracking triggers can be sent over parallel port same as EEG TTL

## TTL Parallel Port Triggers 
 * `inpout32.dll` should be in directory where python runs `from psychopy import parallel`
 * used to mark task events EEG or ASL eye tracking


## Images
Selection made with `img_pick.py`:
```
# r,g,b all .1 from equal. percieved brightness around 1std of the mean
q = d.query('abs(r-.33) < .1 and abs(g-.33) < .1 and abs(b-.33) <.1 and abs(p-116) < 10 ')
```
after `imgedit.py` (help from `SUN/iminfo.py`) converted images into `225x225` circle pngs.

### More images
2017-12-07: identified 635 more browsing in alphabetical order
2018-11-27: removed some w/help from anna,`remove_c.bash` from [(list)](https://docs.google.com/spreadsheets/d/1U_CWaaSiaHqn59llR-xTQ-VhvngGJDUFqUBpA8H7d7w/edit?usp=sharing)

### image source 
Images are from [SUN](http://vision.princeton.edu/projects/2010/SUN) dataset. 
 * [all images](http://vision.princeton.edu/projects/2010/SUN/SUN397.tar.gz) (37Gb!, 38 uncompressed)
 * [3 level hierarchy annotation](http://vision.cs.princeton.edu/projects/2010/SUN/hierarchy_three_levels.zip) (<1Mb)

## Data analysis
are ttl triggers reporting resonable times? `eeg/read.py`
