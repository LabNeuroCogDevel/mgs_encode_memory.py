#!/usr/bin/env bash
set -e
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT
cd $(dirname 0)

#
# calc efficiency score for all timings
#
tr=2
ntrs=210 # 420/2


outdir=$(pwd)/decon_txtout
[ ! -d $outdir ] && mkdir $outdir
for d in $(pwd)/mri/*/; do
   cd $d
   pwd
   saveprefix=$outdir/$(basename $d)_

   3dDeconvolve -nodata $ntrs $tr \
      -num_stimts 14 \
      -stim_times_AM1  1 vgs_NearLeft_Indoor.1D   'dmUBLOCK' -stim_label  1 vgs_NearLeft_Indoor  \
      -stim_times_AM1  2 vgs_NearLeft_None.1D     'dmUBLOCK' -stim_label  2 vgs_NearLeft_None    \
      -stim_times_AM1  3 vgs_NearLeft_Outdoor.1D  'dmUBLOCK' -stim_label  3 vgs_NearLeft_Outdoor \
      -stim_times_AM1  4 vgs_Left_Indoor.1D       'dmUBLOCK' -stim_label  4 vgs_Left_Indoor  \
      -stim_times_AM1  5 vgs_Left_None.1D         'dmUBLOCK' -stim_label  5 vgs_Left_None    \
      -stim_times_AM1  6 vgs_Left_Outdoor.1D      'dmUBLOCK' -stim_label  6 vgs_Left_Outdoor \
      -stim_times_AM1  7 vgs_NearRight_Indoor.1D  'dmUBLOCK' -stim_label  7 vgs_Right_Indoor \
      -stim_times_AM1  8 vgs_NearRight_None.1D    'dmUBLOCK' -stim_label  8 vgs_Right_None   \
      -stim_times_AM1  9 vgs_NearRight_Outdoor.1D 'dmUBLOCK' -stim_label  9 vgs_Right_Outdoor\
      -stim_times_AM1 10 vgs_Right_Indoor.1D      'dmUBLOCK' -stim_label 10 vgs_NearRight_Indoor \
      -stim_times_AM1 11 vgs_Right_None.1D        'dmUBLOCK' -stim_label 11 vgs_NearRight_None   \
      -stim_times_AM1 12 vgs_Right_Outdoor.1D     'dmUBLOCK' -stim_label 12 vgs_NearRight_Outdoor\
      -stim_times_AM1 13 dly.1D                   'dmUBLOCK' -stim_label 13 dly              \
      -stim_times_AM1 14 mgs.1D                   'dmUBLOCK' -stim_label 14 mgs              \
      -num_glt 7\
      -gltsym "SYM: +vgs_Left_Indoor -vgs_NearLeft_Outdoor +vgs_NearRight_Indoor  -vgs_NearRight_Outdoor +vgs_Left_Indoor -vgs_Left_Outdoor +vgs_Right_Indoor  -vgs_Right_Outdoor" -glt_label 1 in_out \
      -gltsym "SYM: 0.5*vgs_NearLeft_Indoor 0.5*vgs_NearLeft_Outdoor 0.5*vgs_NearRight_Indoor  0.5*vgs_NearRight_Outdoor -vgs_NearLeft_None -vgs_NearRight_None 0.5*vgs_Left_Indoor 0.5*vgs_Left_Outdoor 0.5*vgs_Right_Indoor  0.5*vgs_Right_Outdoor -vgs_Left_None -vgs_Right_None" -glt_label 2 some_none \
      -gltsym "SYM: +vgs_NearLeft_Indoor +vgs_NearLeft_None +vgs_NearLeft_Outdoor +vgs_NearRight_Indoor +vgs_NearRight_None +vgs_NearRight_Outdoor +vgs_Left_Indoor +vgs_Left_None +vgs_Left_Outdoor +vgs_Right_Indoor +vgs_Right_None +vgs_Right_Outdoor" -glt_label 3 vgs \
      -gltsym "SYM: 0.11*vgs_NearLeft_Indoor  0.11*vgs_NearLeft_None  0.11*vgs_NearLeft_Outdoor 0.11*vgs_NearRight_Indoor 0.11*vgs_NearRight_None 0.11*vgs_NearRight_Outdoor  0.11*vgs_Left_Indoor  0.11*vgs_Left_None  0.11*vgs_Left_Outdoor 0.11*vgs_Right_Indoor 0.11*vgs_Right_None 0.11*vgs_Right_Outdoor -dly" -glt_label 4 vgs_dly \
      -gltsym "SYM: 0.11*vgs_NearLeft_Indoor  0.11*vgs_NearLeft_None  0.11*vgs_NearLeft_Outdoor 0.11*vgs_NearRight_Indoor 0.11*vgs_NearRight_None 0.11*vgs_NearRight_Outdoor 0.11*vgs_Left_Indoor  0.11*vgs_Left_None  0.11*vgs_Left_Outdoor 0.11*vgs_Right_Indoor 0.11*vgs_Right_None 0.11*vgs_Right_Outdoor -mgs" -glt_label 5 vgs_mgs \
      -gltsym "SYM: +dly -mgs" -glt_label 6 dly_mgs \
      -gltsym "SYM: +vgs_Left_Indoor +vgs_NearLeft_Outdoor -vgs_NearRight_Indoor  -vgs_NearRight_Outdoor +vgs_Left_Indoor +vgs_Left_Outdoor -vgs_Right_Indoor  -vgs_Right_Outdoor" -glt_label 7 left_right \
      -x1D X.xmat.1D |
   tee ${saveprefix}convolve.txt

   1d_tool.py -cormat_cutoff 0.1 -show_cormat_warnings -infile X.xmat.1D | 
   tee ${saveprefix}timing.txt

done

# collect all conv files into one file
perl -MFile::Basename -lne '$key=$2 if /(Gen|Stim).*: ([^ ]*)/; $h{basename($ARGV,"_convolve.txt")}{"${key}_$1"}=$2 if /^\W+(LC|h).*=.*?([0-9.]+)/;END{@vals=(keys %{$h{(keys %h)[0]}}); print join("\t","file",@vals); for my $f (keys %h){%_h = %{$h{$f}}; print join("\t",$f, @_h{@vals} )  } }'  decon_txtout/*_convolve.txt > mri_decon.txt
