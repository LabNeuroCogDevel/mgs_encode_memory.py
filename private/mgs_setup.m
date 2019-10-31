function [w, hid, et] = mgs_setup(p_id)
 addpath('/home/abel/matlabTasks/taskHelperFunctions/')
 if ismember('test',{p_id})
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
    etname = p_id(1:min(length(p_id),8));
    et = setup_eyelink(etname, w); % TODO: if fail, set et to zero?
 end
end