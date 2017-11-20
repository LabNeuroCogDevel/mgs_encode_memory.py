#!/usr/bin/env python2
import psychopy.visual as v
import psychopy.event as e

win = v.Window(size=[400,400])
go=True
while(go):
    k=e.waitKeys()
    print(k)
    if 'escape' in k:
        go=False
        
