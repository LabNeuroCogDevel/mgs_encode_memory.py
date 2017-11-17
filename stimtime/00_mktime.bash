#!/usr/bin/env bash

[ -d stims ] && rm -r stims
genTaskTime  -o stims '<300/30> vgs=[1.5](Left,Right * Indoor,Outdoor,None); dly=[15x 1.5, 10x 2, 3x 3, 2x 4 ]; mgs=[1.5]'
