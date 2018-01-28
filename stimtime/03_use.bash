#!/usr/bin/env bash

# 20180128 -- use top 2 of s6e6_neverfirst
sed 1d mri_decon/s6e6_neverfirst_20.txt |
 cut -f1 |
 while read seed; do 
    cp -r mri/s6e6_neverfirst/$seed ../stims/mri/;
done

