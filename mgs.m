function mgs(subj)
  % clear everything
  %  sca; close all; clearvars;
  if nargin < 1
      subj = input('participant id: ','s');
  end
  
  % initialze screen, DAQ, and eyetracking
  [w, hid, et] = mgs_setup(subj);
  % if eyetracking, what do we tell the eye tracker when we start
  if et, startmsg = 'START'; else, startmsg=''; end
  
  % read "1D" onset:duration files and sort:[onset, duration] + {event}
  [onsets, event] = read_stims('stims/ieeg/3479197962273054302');
  
  % initialze with fixation
  trial = 1;
  prep_event(w, 'fix')
  
  % start with 500ms of fix
  screenstart = Screen('Flip', w);
  send_triggers(hid, 0, startmsg);
  starttime = screenstart + .5;
  
  for eidx=1:length(onsets)
      
      % event prep
      this_e = event{eidx};
      prep_event(w, this_e);
      [ttl, ttlmsg] = calc_ttl(this_e, trial, et);
      etime = Screen('Flip', w, starttime + onsets(eidx,1));
      send_triggers(hid, ttl, ttlmsg);
      
      % last event of a trail is mgs
      % followed by fix (but not in onset times)
      if strncmp(this_e, 'mgs', 3)
          trial = trial + 1;
          % do fix between trials
          fixon = etime + onsets(eidx,2);
          prep_event(w, 'fix')
          [ttl, ttlmsg] = calc_ttl('fix', trial, et);
          Screen('Flip', w, fixon); % mgs dur is always 2s
          send_triggers(hid, ttl, ttlmsg)
      end
  end
end