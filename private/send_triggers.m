function send_triggers(hid, TTL, ttlstr)
  if hid > 0
      DaqDOut(hid, 0, TTL);
  end
  if ttlstr
      Eyelink('Message', ttlstr);
  end
end