function [etime fixon_flip] = task_event(hid, w, et, e, ntrials)
   % run an MGS event
   %
   %  runs: prep_vent, calc_ttl, Flip, send_trigger, fix (if event='mgs')
   %
   %  % save output
   %  eventtimes(trial).(this_e) = etime;
   %  save(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');

   % fixon only for last trial event type (mgs)
   fixon_flip = NaN;
   
   %% event prep - events are: cue vgs dly mgs
   % only vgs has a non-empty texture
   prep_event(w, e.name, e.tex);
   [ttl, ttlmsg] = calc_ttl(e.name, e.trial, et);
   % we hang out here for a bit -- flipping after some delay @ "onset"
   etime = Screen('Flip', w, e.onset);
   send_triggers(hid, ttl, ttlmsg);
   
   fprintf('%d/%d (blk %d): %s for %.2f @ %.2f (%.3f)\n',...
           e.trial, ntrials, e.cblock, e.name, e.dur, ...
           e.rel_onset, etime);
   
   % last event of a trail is mgs
   % should be followed by fix (but not in onset times)
   % mgs delay is always 2 
   if strncmp(e.name, 'mgs', 3)
       % do fix between trials
       fixon = etime + e.dur;
       fixon_flip = showfix(w, e.trial, hid, et, fixon);
       % done outside this function
       % eventtimes(trial).fix = fixon_flip;
   end
end
