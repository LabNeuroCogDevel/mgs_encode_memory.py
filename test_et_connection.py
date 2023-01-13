#!/usr/bin/env python3
#
# put me in client folder with VPX_InterApp, e.g. 'VPx32-Client' 
# run me with test_et.bat (as shortcut or copied directly to desktop)
#
# 20230113 - used to debug msg.encode('ascii') issue
vpxDll = 'VPX_InterApp_32.dll'
from ctypes import cdll, CDLL
cdll.LoadLibrary(vpxDll)
vpx = CDLL(vpxDll)
print("status: %d" % vpx.VPX_GetStatus(1))
print("sending hello message")
vpx.VPX_SendCommand('say "PY VPX DLL TEST"'.encode('ascii'))
