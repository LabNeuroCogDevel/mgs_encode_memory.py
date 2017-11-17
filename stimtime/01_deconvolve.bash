#!/usr/bin/env bash
set -e
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT
cd $(dirname 0)

#
# calc efficiency score for all timings
#
tr=2
ntrs=150 # 300/2


[ ! -d txt ] && mkdir txt
for d in $(pwd)/stims/*/; do
   cd $d

   3dDeconvolve -nodata $ntrs $tr \
      -num_stimts 8 \
      -stim_times_AM1 1 vgs_Left_Indoor   'dmUBLOCK' -stim_label 1 vgs_Left_Indoor  \
      -stim_times_AM1 2 vgs_Left_None     'dmUBLOCK' -stim_label 2 vgs_Left_None    \
      -stim_times_AM1 3 vgs_Left_Outdoor  'dmUBLOCK' -stim_label 3 vgs_Left_Outdoor \
      -stim_times_AM1 4 vgs_Right_Indoor  'dmUBLOCK' -stim_label 4 vgs_Right_Indoor \
      -stim_times_AM1 5 vgs_Right_None    'dmUBLOCK' -stim_label 5 vgs_Right_None   \
      -stim_times_AM1 6 vgs_Right_Outdoor 'dmUBLOCK' -stim_label 6 vgs_Right_Outdoor\
      -stim_times_AM1 7 dly               'dmUBLOCK' -stim_label 7 dly              \
      -stim_times_AM1 8 mgs               'dmUBLOCK' -stim_label 8 mgs              \
      -num_glt 6\
      -gltsym "SYM: +vgs_Left_Indoor -vgs_Left_Outdoor +vgs_Right_Indoor  -vgs_Right_Outdoor" -glt_label 1 in_out \
      -gltsym "SYM: 0.5*vgs_Left_Indoor 0.5*vgs_Left_Outdoor 0.5*vgs_Right_Indoor  0.5*vgs_Right_Outdoor -vgs_Left_None -vgs_Right_None" -glt_label 2 some_none \
      -gltsym "SYM: +vgs_Left_Indoor +vgs_Left_None +vgs_Left_Outdoor +vgs_Right_Indoor +vgs_Right_None +vgs_Right_Outdoor" -glt_label 3 vgs \
      -gltsym "SYM: 0.17*vgs_Left_Indoor  0.17*vgs_Left_None  0.17*vgs_Left_Outdoor 0.17*vgs_Right_Indoor 0.17*vgs_Right_None 0.17*vgs_Right_Outdoor -dly" -glt_label 4 vgs_dly \
      -gltsym "SYM: 0.17*vgs_Left_Indoor  0.17*vgs_Left_None  0.17*vgs_Left_Outdoor 0.17*vgs_Right_Indoor 0.17*vgs_Right_None 0.17*vgs_Right_Outdoor -mgs" -glt_label 5 vgs_mgs \
      -gltsym "SYM: +dly -mgs" -glt_label 6 dly-mgs \
      -x1D X.xmat.1D |
   tee convolve.txt

   1d_tool.py -cormat_cutoff 0.1 -show_cormat_warnings -infile X.xmat.1D | 
   tee timing.txt


   #break
done








