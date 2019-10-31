function [w, hid, et] = mgs_setup(subj)
 addpath('/home/abel/matlabTasks/taskHelperFunctions/')
 et = 1; % default to using
 if ismember('test',{subj})
     bg = [0 0 0];
     screen = 0;
     res = [0 0 800 600];
     w = Screen('OpenWindow', screen, bg, res);
     hid = 0;
     et = 0;
 else
    hid = DaqFind;
    [w,~] = initializeScreen();
    DaqDOut(hid,0,0);
    % max 9char name
    subjetname = subj(1:min(length(subj),9));
    setup_eyelink(subjetname); % TODO: if fail, set et to zero?
 end
end