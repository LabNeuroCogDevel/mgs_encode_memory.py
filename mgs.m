function mgs(subj, imgset)
  % clear everything
  %  sca; close all; clearvars;

  if nargin < 1
      subj = input('participant id: ','s');
  end
  if nargin < 2
      imgset = input('imgset (A|B): ','s');
      validatestring(imgset,{'A','B','C'});
  end

  % initialze screen, DAQ, and eyetracking
  [w, hid, et] = mgs_setup(subj);
  % if eyetracking, what do we tell the eye tracker when we start
  if ~isempty(et), startmsg = 'START'; else, startmsg=''; end
  
  % read "1D" onset:duration files and sort:[onset, duration] + {event}
  [onsets, events] = read_stims('stims/ieeg/3479197962273054302');
  
  % make textures for events that need it
  [event_tex, imgs_used] = make_textures(w, events, imgset);
  
  % show instructions
  instructions(w)
  
  % how to save 
  savename = [subj '_' imgset '_' datestr(now(),'yyyymmddHHMMSS')];
  savefile = fullfile('subj_info/ieeg/',[savename '.mat']);
  save(savefile, 'onsets', 'events', 'imgs_used');
  
  % start eye recording
  if ~isempty(et), Eyelink('StartRecording'); end
  
  % initialze with fixation
  trial = 1;
  prep_event(w, 'fix')
  
  % start with 500ms of fix
  screenstart = Screen('Flip', w);
  send_triggers(hid, 0, startmsg);
  starttime = screenstart + .5;
  
  % stuct for storing onset times
  eventtimes = struct();
  %ntrial = length(onsets);
  ntrial = 24; % TODO: insert breaks
  for eidx=1:ntrial
      
      % event prep - events are: cue vgs dly mgs
      this_e = events{eidx};
      prep_event(w, this_e, event_tex(eidx));
      [ttl, ttlmsg] = calc_ttl(this_e, trial, et);
      etime = Screen('Flip', w, starttime + onsets(eidx,1));
      send_triggers(hid, ttl, ttlmsg);
      
      fprintf('%d/%d: %s for %.2f @ %f\n', trial, ntrial, this_e, onsets(eidx,2), etime)
      
      % last event of a trail is mgs
      % followed by fix (but not in onset times)
      if strncmp(this_e, 'mgs', 3)
          trial = trial + 1;
          % do fix between trials
          fixon = etime + onsets(eidx,2);
          prep_event(w, 'fix')
          [ttl, ttlmsg] = calc_ttl('fix', trial, et);
          fixon = Screen('Flip', w, fixon); % mgs dur is always 2s
          send_triggers(hid, ttl, ttlmsg)
          fprintf('fix @ %f\n', fixon)
          eventtimes(trial).fix = fixon;

      end
      
      % save output
      eventtimes(trial).(this_e) = etime;
      save(savefile, 'onsets','events', 'imgs_used','starttime', 'eventtimes', 'trial');
      %fprintf('saved to %s @ %f\n', savefile,  GetSecs())
  end
  
  % stop recording
  if ~isempty(et), Eyelink('StopRecording'); end
  % have a lot of textures open, close them
  Screen('CloseAll')
end