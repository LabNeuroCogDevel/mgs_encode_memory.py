function send_triggers(hid, et, e)
  if strncmp(e, 'fix', 3)
      TTL=10;
  elseif strncmp(e, 'cue', 3)
      TTL=50;
  elseif strncmp(e, 'vgs', 3)
      TTL=100;
  elseif strncmp(e, 'dly', 3) || strncmp(e, 'isi', 3)
      TTL=150;
  elseif strncmp(e, 'mgs', 3)
      TTL=200;
  else
      error('unknown event %s', e)
  end
end