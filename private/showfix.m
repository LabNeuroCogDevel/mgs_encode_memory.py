function fixon_flip = showfix(w, trial, hid, et, fixon)
  prep_event(w, 'fix')
  [ttl, ttlmsg] = calc_ttl('fix', trial, et);
  fixon_flip = Screen('Flip', w, fixon); % mgs dur is always 2s
  send_triggers(hid, ttl, ttlmsg)
  fprintf('fix @ %f\n', fixon_flip)
end