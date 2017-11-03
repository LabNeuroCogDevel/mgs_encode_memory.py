#!/usr/bin/env bash
set -e
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT

#
# 
#
savedir=select_$(date +%F)
[ ! -d $savedir ] && mkdir $savedir

annot="./levels.txt"
cut -f 3 $annot|sort|uniq | while read field; do
   fieldprint=${field//[, ]/}
   for cat in $(grep "$field" $annot | shuf | head -n 20|cut -f1); do 
      catprint=$fieldprint${cat//\//_}
      for img in $(find SUN397/$cat -maxdepth 1 -iname '*jpg'|shuf | head -n2); do
         echo $savedir/$catprint.jpg
         cp $img $savedir/$catprint.jpg
      done
   done
done
