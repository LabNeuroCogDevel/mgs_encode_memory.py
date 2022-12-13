2022-12-13 WF 
 - Needed VCDist_x86 2013 for 32bit viewpoint client
 - Psychopy version is 3.0.0 (2018)
   Python 3.6.5 (v3.6.5:f59c0932b4, Mar 28 2018, 16:07:46) [MSC v.1900 32 bit (Intel)] on win32
 - OS: Win7 2009SP1 64bit (i5-3450, 8GB ram)

2022-12-12 WF 
 - 32bit VP client needs MSVCP120.dll
 - copy task. small edits. needed MSVC x64 2017. using 32bit python. 
 - might need 64 to talk to viewpoint 64 (but cant get that to run)
 - 32bit python with 64bit dll: OSError: [WinError 193] %1 is not a valid Win32 application
    self.vpxDll = 'C:\\Users\\Luna\\Desktop\\VPx64-Client\\VPX_InterApp_64.dll'
 - can run without eyetracking
