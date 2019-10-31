function mgs()
  [w, hid, et] = mgs_setup();
  
  [onsets, event] = read_stims('stims/ieeg/3479197962273054302');
  
  trial = 1;
  prep_event(w, 'fix')
  
  % start with 500ms of fix 
  starttime = Screen('Flip',w) + .5;
  for eidx=1:length(onsets)
      this_e = event{eidx};
      prep_event(w, this_e);
      % Screen('DrawingFinished', w);
      etime = Screen('Flip', w, starttime + onsets(eidx,1));
      send_triggers(hid, et, this_e);
      
      if strncmp(this_e, 'mgs', 3)
          trial = trial + 1;
          % do fix between trials
          fixon = etime + onsets(eidx,2);
          prep_event(w, 'fix')
          Screen('Flip', w, fixon); % mgs dur is always 2s
          send_triggers(hid, et, 'fix')
      end
  end
end