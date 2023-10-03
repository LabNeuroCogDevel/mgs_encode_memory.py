# MGS Encode circa 2018

MR Memory guided saccade task run from 2005-2019.

Reported in ["The expression of established cognitive brain states stabilizes with working memory development" (2017)](https://elifesciences.org/articles/25606)

EPrime1 tasks copied at the end of "CogLong" when NIC scanner shutdown.

Eye recordings were with ASL Model 5000 Long Range Optics

## Timing

  * MR acquisition is `229` volumes at `1.5` seconds TR.
  * Short delay is `1.5` seconds. Long delay is `9` seconds. 
  * Short cue is 1.5` seconds. Long cue is `3` seconds. 
  * Fix (ITI) is `1.5` for each repeat (stacked for variable length ITI).

### example

Here's the event list extracted from `MGS Encode - v. 1.es`. Repeat `Fix` events are distributed to optomize HRF.
MGS Encode 1 - 3 only vary in the order and distribution of these events.


|n|`event_name_and_eye_pos`|`horz_position_0_640`|
|-|------------------------|---------------------|
|1|LongCueShortDelay108|108|
|6|Fix| |
|1|LongCueLongDelay7|7|
|5|Fix| |
|1|ShortCueLongDelay214|214|
|6|Fix| |
|1|LongCueLongDelay532|532|
|3|Fix| |
|1|ShortCueLongDelay7|7|
|6|Fix| |
|1|ShortCueShortDelay108|108|
|2|Fix| |
|1|LongCueShortDelay426|426|
|6|Fix| |
|1|ShortCueShortDelay426|426|
|3|Fix| |
|1|LongCueLongDelay214|214|
|2|Fix| |
|1|LongCueShortDelay633|633|
|3|Fix| |
|1|LongCueLongDelay426|426|
|5|Fix| |
|1|ShortCueLongDelay108|108|
|7|Fix| |
|1|ShortCueShortDelay7|7|
|5|Fix| |
|1|LongCueShortDelay532|532|
|3|Fix| |
|1|LongCueLongDelay108|108|
|4|Fix| |
|1|ShortCueLongDelay532|532|
|2|Fix| |
|1|ShortCueShortDelay633|633|
|5|Fix| |
|1|LongCueShortDelay214|214|
|3|Fix| |
|1|ShortCueLongDelay633|633|
|5|Fix| |
|1|ShortCueShortDelay532|532|
|8|Fix| |



## Files
```
├── MGS Encode - v. 1.es
├── MGS Encode - v. 2.es
├── MGS Encode - v. 3.es
└── example_data
    └── 10248
        ├── 20070407
        │   └── Raw
        │       ├── EPrime
        │       │   ├── 10248_20070407_MGS Encode - v-5835-1.edat
        │       │   └── 10248_20070407_MGS Encode - v-5835-1.txt
        │       └── EyeData
        │           ├── 10248_5835_mgsencode1.eyd
        │           ├── 10248_5835_mgsencode2.eyd
        │           └── 10248_5835_mgsencode3.eyd
        └── 20190511
            └── Raw
                ├── EPrime
                │   ├── MGS Encode - v-10248-29.edat
                │   ├── MGS Encode - v-10248-29.txt
                │   ├── MGS Encode - v-10248-30.edat
                │   ├── MGS Encode - v-10248-30.txt
                │   ├── MGS Encode - v-10248-31.edat
                │   └── MGS Encode - v-10248-31.txt
                └── EyeData
                    ├── 10248_mgsencode_run1.eyd
                    ├── 10248_mgsencode_run2.eyd
                    └── 10248_mgsencode_run3.eyd
 
```

### MR
see [`dicom_hdr.txt`](dicom_hdr.txt)

```
dcmdirtab -d '/Volumes/Hera/Raw/MRprojects/CogLong/190312152607/*/' > dicom_hdr.txt
```

### Usage
```
ls /Volumes/L/bea_res/Data/Tasks/MGSEncode/Basic/1*/2* | sed s:.*/:: |cut -c1-4|sort|uniq -c
```

|n sessions|year|
|----------|----|
|31| 2005|
|71| 2006|
|85| 2007|
|56| 2008|
|58| 2009|
|58| 2010|
|16| 2011|
|34| 2012|
|40| 2013|
|29| 2014|
|30| 2015|
|29| 2016|
|19| 2017|
|14| 2018|
| 4| 2019|
