function savefile = mgs(subj, imgset, nblock, use_et)
  % clear everything
  %  sca; close all; clearvars;

  % subject - any string
  if nargin < 1
      subj = input('participant id: ','s');
  end
  % imageset - A, B, C
  if nargin < 2
      imgset = input('imgset (A|B): ','s');
  end
  % nuber of runs/blocks - probably 3
  if nargin < 3
      nblock = input('number of runs (3) [ignored if resume]: ');
      if isempty(nblock)
          nblock=3;
      end
  end
  % should we use eyetracking?
  if nargin < 4
      fprintf('MAKE SURE EYE IS TRACKED/IDed by eyelink\n')
      use_et = input('use eyetracking (1|0, defulat to 1): ');
      if isempty(use_et)
          use_et=1;
      end
  end

  % validate input
  validatestring(imgset,{'A','B','C'});

  % initialze (or reset current block of) a matfile that we will load from/save to
  savefile = resume_or_new(subj, imgset, nblock);
  load(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');

  % some settings
  ntrials = max([event_info.trial]);
  nblocks = max([event_info.block]);
  cblock = event_info.block(trial);
  
  % initialze screen, DAQ, and eyetracking
  [w, hid, et] = mgs_setup(subj, use_et);
  % if eyetracking, what do we tell the eye tracker when we start
  if ~isempty(et), startmsg = 'START'; else, startmsg=''; end
    
  % make textures for events that need it
  event_tex = make_textures(w, imgs_used, event_info.events);
  
  % show instructions
  instructions(w)
  
  % start eye recording
  if ~isempty(et), Eyelink('StartRecording'); end
  
  % initialze with fixation
  prep_event(w, 'fix')
  
  % start with 500ms of fix
  start_delay=.5;
  screenstart = Screen('Flip', w);
  send_triggers(hid, 0, startmsg);

  % half second of fix before start
  starttime(cblock) = screenstart + start_delay;
  nevents = length(event_info.onsets);
  for eidx=trial:nevents
      
      % get event info. including e.name, e.trial, and e.cblock
      % extract from events, blocks, 
      e = event_from_info(event_info, starttime, event_tex, eidx);

      % run event: presentation, flip, triggers, and fixation (if mgs)
      % returns event onset time, and fixonset (NaN if not mgs)
      [etime fixon_flip] = task_event(hid, w, et, e, ntrials)

      % save output
      if ~isnan(fixon_flip), eventtimes(e.trial).fix = fixon_flip; end
      eventtimes(e.trial).(e.name) = etime;
      save(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');
      %fprintf('saved to %s @ %f\n', savefile,  GetSecs())
      
      % starting new block
      if cblock ~= event_info.block(min(eidx+1,nevents))
          WaitSecs(.5); % show last fixation for half a second
          msg = sprintf('Finished %d/%d!', cblock, nblocks);
          ttlmsg='';
          if ~isempty(et), ttlmsg=sprintf('BLOCKEND%d',e.cblock); end
          send_triggers(hid, 0, ttlmsg);
          keyhit = disp_til_key(w, msg);
          % show fix for .5 seconds
          fixon_flip = showfix(w, e.trial, hid, et, keyhit);
          cblock = event_info.block(eidx+1);
          starttime(cblock) = fixon_flip + .5;
      end
  end
  
  % stop recording
  if ~isempty(et), Eyelink('StopRecording'); end
  disp_til_key(w, 'Finished!\n Thank you!!')
  % have a lot of textures open, close them
  Screen('CloseAll')
end
