disp('DAQ TTL')
hid = DaqFind;
DaqDOut(hid, 0, 100);

disp('Second monitor')
helpdir='/home/abel/matlabTasks/taskHelperFunctions/';
addpath(helpdir)
disp('running initializeScreen from taskHerlperFuncions (2nd screen)')
[w,~] = initializeScreen();
disp('success')

disp('ping ET')
system('ip addr list')
system('ping -c 1 100.1.1.1')
