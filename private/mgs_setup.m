function [w, hid, et] = mgs_setup(p_id, use_et, skip_hid)

 % setup keys - potentioally undo recall key restrictions
 KbName('UnifyKeyNames');
 RestrictKeysForKbCheck([]);

 % defaults to not using any externals
 hid = 0;
 et = [];
 if nargin < 2, use_et = 0; end
 % but if use_hid is 0, we dont need to prompt
 if nargin < 3, skip_hid = 0; end

 % the 'test' subject is special
 if ismember('test',{p_id})
     w = testscreen();
     return
 end

 % initializeScreen from presentation computer
 % if we dont have it, we are testing
 helpdir='/home/abel/matlabTasks/taskHelperFunctions/';
 if ~exist(helpdir, 'dir')
     w = testscreen();
     fprintf('WARNING: could not find taskHelperFunctions!')
 else
    addpath(helpdir)
    disp('running initializeScreen from taskHerlperFuncions (2nd screen)')
    [w,~] = initializeScreen();
    disp('connected to second screen')
 end
 
 %% do we send a trigger
if skip_hid
  fprintf('contining without DAQ and not trying!\n')
else
   try
      hid = DaqFind;
      DaqDOut(hid,0,0);
   catch e
        quitwithout('DAQ TTL triggers', e)
   end
end
 
 % do we really want eye tracking?
 if ~use_et
    return
 end
 
 %% try to setup eyetracking
 % if it fails offer to continue
 % but default to crashing
 
 % max 8char name
 etname = p_id(1:min(length(p_id),8));
 try
   et = setup_eyelink(etname, w); % TODO: if fail, set et to zero?
 catch e
   % failed! continue?
   quitwithout('eye tracking', e)
 end
end

function quitwithout(failedthing, e)
   % show error
   if nargin >= 2
      disp(e)
   end
   % pompt to continue
   msg = sprintf('continue without %s (0=end [default]|1=continue)? ', failedthing);
   cont_anyway = input(msg);
   if cont_anyway ~= 1
      sca
      error('NO %s, decided to not continue!', failedthing)
   end
end

function w = testscreen()
     bg = [0 0 0];
     screen = 0;
     res = [0 0 800 600];
     w = Screen('OpenWindow', screen, bg, res);
end
