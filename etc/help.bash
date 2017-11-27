#!/usr/bin/env bash

# get images from clibpoard, save as png with given prefix ($1). incrementally count images
# optionally provied mime-type extention (default png, consider jpeg)
# N.B. prefix with dots will be translated to _
getimg(){ 
   pfix=$1;
   pfix=${pfix//./_}
   ext=$2; [ -z "$ext" ]  && ext=png
   lastnum=$(ls $pfix*|cut -f2 -d.|sort -nr|sed 1q)
   num=$(printf %02d $[$lastnum +1])
   filen=$pfix.$num.$ext
   #echo "$lastnum->$num $filen"
   xclip -selection clipboard -t image/$ext -o > $filen
}
