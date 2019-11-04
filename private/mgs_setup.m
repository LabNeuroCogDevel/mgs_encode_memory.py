function [w, hid, et] = mgs_setup(p_id)

 if ismember('test',{p_id})
     bg = [0 0 0];
     screen = 0;
     res = [0 0 800 600];
     w = Screen('OpenWindow', screen, bg, res);
     hid = 0;
     et = [];
 else
    hid = DaqFind;
    % initializeScreen from 
    addpath('/home/abel/matlabTasks/taskHelperFunctions/')
    [w,~] = initializeScreen();
    DaqDOut(hid,0,0);
    % max 8char name
    etname = p_id(1:min(length(p_id),8));
    et = setup_eyelink(etname, w); % TODO: if fail, set et to zero?
 end
 
 % doesn't help with circle artifact
 % Screen('BlendFunction', w, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');
 
 KbName('UnifyKeyNames');
 RestrictKeysForKbCheck([]);
end