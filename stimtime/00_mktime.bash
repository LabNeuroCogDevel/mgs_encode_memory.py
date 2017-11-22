#!/usr/bin/env bash

[ -d stims ] && rm -r stims
#genTaskTime  -o stims '<300/30> vgs=[1.5](Left,Right * Indoor,Outdoor,None); dly=[15x 1.5, 10x 2, 3x 3, 2x 4 ]; mgs=[1.5]'
#genTaskTime -v 0  -o ../stims/ -i 2 '<300/24 stepsize:2> vgs=[2](Left,Right * Indoor, Outdoor,None); dly=[13x 6, 7x 8, 4x 10]; mgs=[2]'
genTaskTime -v 0  -o ../stims/ -i 2 '<360/24 stepsize:2 iti:2-10 pad:10+10> vgs=[2](Left,Right * Indoor, Outdoor,None); dly=[13x 6, 7x 8, 4x 10]; mgs=[2]'
