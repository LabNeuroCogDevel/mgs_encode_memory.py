#!/usr/bin/env bash
cd $(dirname $0)
for set in A B; do 
   for type in "in" man nat; do 
      montage -tile 7x7 -label '%t' ../img/$set/*$type*/sun_*png ${type}_$set.pdf
   done
done
