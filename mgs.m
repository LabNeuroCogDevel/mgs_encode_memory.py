function savefile = mgs(subj, imgset, trialsperblock)
  % clear everything
  %  sca; close all; clearvars;

  if nargin < 1
      subj = input('participant id: ','s');
  end
  if nargin < 2
      imgset = input('imgset (A|B): ','s');
  end
%   if nargin < 3
%       trialsperblock = input('trialsperblock: ');
%   end
  validatestring(imgset,{'A','B','C'});

  
  % read "1D" onset:duration files and sort:[onset, duration] + {event}
  %[onsets, events] = read_stims('stims/ieeg/3479197962273054302');
  if strcmp(subj,'test')
      modality='test';
  else
      modality = 'ieeg';
  end
  event_info = read_events(modality);
  event_info.imgset = imgset;
  
  % initialze screen, DAQ, and eyetracking
  [w, hid, et] = mgs_setup(subj);
  % if eyetracking, what do we tell the eye tracker when we start
  if ~isempty(et), startmsg = 'START'; else, startmsg=''; end
    
  % make textures for events that need it
  [event_tex, imgs_used] = make_textures(w, event_info.events, imgset);
  
  % show instructions
  instructions(w)
  
  % how to save 
  savename = [subj '_' imgset '_' datestr(now(),'yyyymmddHHMMSS')];
  savefile = fullfile('subj_info/ieeg/',[savename '.mat']);
  savedir = fileparts(savefile);
  if ~exist(savedir,'dir'), mkdir(savedir); end
  save(savefile, 'event_info', 'imgs_used');
  
  % start eye recording
  if ~isempty(et), Eyelink('StartRecording'); end
  
  % initialze with fixation
  prep_event(w, 'fix')
  
  % start with 500ms of fix
  screenstart = Screen('Flip', w);
  send_triggers(hid, 0, startmsg);
  starttime = screenstart + .5;
  
  % stuct for storing onset times
  eventtimes = struct();
  nevents = length(event_info.onsets);
  ntrials = 24; % TODO: insert breaks
  for eidx=1:nevents
      % event info
      this_e = event_info.events{eidx};
      onset = starttime + event_info.onsets(eidx,1);
      e_dur   = event_info.onsets(eidx,2);
      trial = event_info.trial(eidx);
      
      % event prep - events are: cue vgs dly mgs
      % only vgs has a non-empyt texture
      prep_event(w, this_e, event_tex(eidx));
      [ttl, ttlmsg] = calc_ttl(this_e, trial, et);
      % we hang out here for a bit -- flipping after some delay @ "onset"
      etime = Screen('Flip', w, onset);
      send_triggers(hid, ttl, ttlmsg);
      
      fprintf('%d/%d: %s for %.2f @ %f\n', trial, ntrials, this_e, e_dur, etime)
      
      % last event of a trail is mgs
      % should be followed by fix (but not in onset times)
      % mgs delay is always 2 
      if strncmp(this_e, 'mgs', 3)
          % do fix between trials
          fixon = etime + e_dur;
          prep_event(w, 'fix')
          [ttl, ttlmsg] = calc_ttl('fix', trial, et);
          fixon = Screen('Flip', w, fixon); % mgs dur is always 2s
          send_triggers(hid, ttl, ttlmsg)
          fprintf('fix @ %f\n', fixon)
          eventtimes(trial).fix = fixon;

      end
      
      % save output
      eventtimes(trial).(this_e) = etime;
      save(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');
      %fprintf('saved to %s @ %f\n', savefile,  GetSecs())
      
      if trial >= ntrials
          break
      end
  end
  
  % stop recording
  if ~isempty(et), Eyelink('StopRecording'); end
  % have a lot of textures open, close them
  Screen('CloseAll')
end