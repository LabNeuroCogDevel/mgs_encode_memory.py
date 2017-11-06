#!/usr/bin/env bash
set -e
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT

#
# copy from an example output (select.py)
#

[ -z "$1" -o ! -r "$1" ] && echo "$0 examplefile.txt" && exit 1
outdir=selection/$(date +%F)
[ ! -d $outdir ] && mkdir -p $outdir
# SUN397//b/banquet_hall/sun_brgcyugnbkhhygtq.jpg	/b/banquet_hall	shopping and dining	indoor	300.0	281.0	148.48683632621857	0.388576512455516	0.2861803084223013	0.3252431791221827
cat $1 | while IFS=$'\t' read file cat spec gen w h pbright r g b ; do
   cpto=$(echo ${gen}:${spec}:${cat}| sed 's:[ ,/]::g' )
   cp $file $outdir/$cpto:$(basename $file)
done
