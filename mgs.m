function savefile = mgs(subj, imgset, nblock)
  % clear everything
  %  sca; close all; clearvars;

  if nargin < 1
      subj = input('participant id: ','s');
  end
  if nargin < 2
      imgset = input('imgset (A|B): ','s');
  end
  if nargin < 3
      nblock = input('number of runs (3) [ignored if resume]: ');
      if isempty(nblock)
          nblock=3;
      end
  end

  validatestring(imgset,{'A','B','C'});

  % create a matfile we can load from
  savefile = resume_or_new(subj, imgset, nblock);
  load(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');

  
  % some settings
  ntrials = max([event_info.trial]);
  nblocks = max([event_info.block]);
  cblock = event_info.block(trial);
  
  % initialze screen, DAQ, and eyetracking
  [w, hid, et] = mgs_setup(subj);
  % if eyetracking, what do we tell the eye tracker when we start
  if ~isempty(et), startmsg = 'START'; else, startmsg=''; end
    
  % make textures for events that need it
  [event_tex, imgs_used] = make_textures(w, event_info.events, imgset);
  
  % show instructions
  instructions(w)
  
  % start eye recording
  if ~isempty(et), Eyelink('StartRecording'); end
  
  % initialze with fixation
  prep_event(w, 'fix')
  
  % start with 500ms of fix
  screenstart = Screen('Flip', w);
  send_triggers(hid, 0, startmsg);

  
  starttime(cblock) = screenstart + .5; % half second of fix before start
  % stuct for storing onset times
  eventtimes = struct();
  nevents = length(event_info.onsets);
  for eidx=trial:nevents
      % event info
      this_e = event_info.events{eidx};
      cblock = event_info.block(eidx);
      onset = starttime(cblock) + event_info.onsets(eidx,1);
      e_dur   = event_info.onsets(eidx,2);
      trial = event_info.trial(eidx);
      
      % event prep - events are: cue vgs dly mgs
      % only vgs has a non-empyt texture
      prep_event(w, this_e, event_tex(eidx));
      [ttl, ttlmsg] = calc_ttl(this_e, trial, et);
      % we hang out here for a bit -- flipping after some delay @ "onset"
      etime = Screen('Flip', w, onset);
      send_triggers(hid, ttl, ttlmsg);
      
      fprintf('%d/%d (blk %d): %s for %.2f @ %.2f (%.3f)\n',...
              trial, ntrials, cblock, this_e, e_dur, ...
              event_info.onsets(eidx,1), etime);
      
      % last event of a trail is mgs
      % should be followed by fix (but not in onset times)
      % mgs delay is always 2 
      if strncmp(this_e, 'mgs', 3)
          % do fix between trials
          fixon = etime + e_dur;
          fixon_flip = showfix(w, trial, hid, et, fixon);
          eventtimes(trial).fix = fixon_flip;
      end
      
      % save output
      eventtimes(trial).(this_e) = etime;
      save(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');
      %fprintf('saved to %s @ %f\n', savefile,  GetSecs())
      
      % starting new block
      if cblock ~= event_info.block(min(eidx+1,nevents))
          WaitSecs(.5); % show last fixation for half a second
          msg = sprintf('Finished %d/%d!', cblock, nblocks);
          ttlmsg='';
          if ~isempty(et), ttlmsg=sprintf('BLOCKEND%d',cblock); end
          send_triggers(hid, 0, ttlmsg);
          disp_til_key(w, msg);
          % show fix for .5 seconds
          fixon_flip = showfix(w, trial, hid, et, fixon);
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