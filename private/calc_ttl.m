function [TTL, msg] = calc_ttl(e, trl, et)
% calculate TTL and eye tracking event message
  trl = num2str(trl);
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
  
  % must be numbers and letters only
  if et
      msg = [regexprep(e,'[^A-za-z0-9]',''), trl];
  else
      msg = '';
 end