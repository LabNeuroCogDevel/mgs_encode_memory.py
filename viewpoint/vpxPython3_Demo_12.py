# ViewPoint EyeTracker (R) interface to Python 3 (vpxPython3_Demo_09.py)
#       Verify the sections below marked:       # <<<< CHANGE AS NEEDED
#	Paths must use either (a) Forward Slashes, or (b) Double Back Slashes !!!
#	To use Python 2 change: print("x") --to--> print "x"
#	07-Dec-2010 : kfa : changed to Python3 and added vpxDll access check.
#
#	To run this, either put this file in the Python root directory, or do:
#		import sys			# to set where to look for modules
# 		sys.path.append("C:/ARI/VP")	# <<<< CHANGE AS NEEDED
# 		import vpxPython3_Demo  	# <<<< CHANGE AS NEEDED, without .py
#
#	This demo prints a line whenever an ROI is newly entered or exited.
#	Nothing is printed while the the gaze point remains inside an ROI.
#	Example: 	[3,19] means the gaze point just entered ROI#3 and ROI#19,
#			[-3] means the gazepoint has just exited ROI#3
#

from ctypes import *
import os

#  CONSTANTS (see vpx.h for full listing)
VPX_STATUS_ViewPointIsRunning = 1
EYE_A = 0
VPX_DAT_FRESH = 2

#
#  Load the ViewPoint library
vpxDll = "C:/ARI/VP/VPX_InterApp.dll"	# <<<< CHANGE AS NEEDED
if ( not os.access(vpxDll,os.F_OK) ):
	print("WARNING: Invalid vpxDll path; you need to edit the .py file")
cdll.LoadLibrary( vpxDll )
vpx = CDLL( vpxDll )
vpx.VPX_SendCommand('say "Hello from Python" ')
if ( vpx.VPX_GetStatus(VPX_STATUS_ViewPointIsRunning) < 1 ):
	print("ViewPoint is not running")
#
#  Create needed structures and and callback function
class RealPoint(Structure):
	_fields_ = [("x",c_float),("y",c_float)]

	# Need to declare a RealPoint variable
gp = RealPoint(1.1,1.1)

VPX_CALLBACK = CFUNCTYPE( c_int, c_int, c_int, c_int, c_int )
	# 	The first param is the return value, the rest function parameters.

def ViewPointMessageCallback( msg, subMsg, p1, p2, ):
	if ( msg == VPX_DAT_FRESH ):
		roiList = []
		for ix in range(5):
			roiNumber = vpx.VPX_ROI_GetEventListItem( EYE_A, ix )
			if (roiNumber != -9999):
				roiList.append(roiNumber)
			else:
				break
		if (len(roiList)>0):
			print(roiList)
	return 0
#
#  Register the Python callback function with the ViewPoint DLL
vpxCallback = VPX_CALLBACK(ViewPointMessageCallback)
vpx.VPX_InsertCallback(vpxCallback)

