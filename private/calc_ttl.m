function [TTL, msg] = calc_ttl(e, trl, et)
% calculate TTL and eye tracking event message
% python code -- followed only for img/vgs
%     # ttl codes are a composit of the event, and image side + catagory
%     # allow unspecified triggers as 0
%     # outside of 0, range is 61 (cue:None,Left) to 234 (mgs:Indoor,Right)
%     # cues  < 100 (61 -> 84); img < 150 (111 -> 134);
%     # isi < 200 ( 161 -> 184); mgs < 250 (211->234)
%     event_dict = {'bad': 0, 'cue': 50, 'img': 100, 'isi': 150, 'mgs': 200}
%     ctgry_dict = {'bad': 0, 'None': 10, 'Outdoor': 20, 'Indoor': 30}
%     side_dict = {'bad': 0, 'Left': 1,
%                  'NearLeft': 2, 'NearRight': 3, 'Right': 4}


  trl = num2str(trl);
  if strncmp(e, 'fix', 3)
      TTL=10;
  elseif strncmp(e, 'cue', 3)
      TTL=50;
  elseif strncmp(e, 'vgs', 3) % || strncmp(e, 'img', 3)
      
      % img pos
      if ~isempty(regexp(e, 'Left','once'))
          TTL=1;
      elseif ~isempty(regexp(e, 'NearLeft','once'))
          TTL=2;
      elseif ~isempty(regexp(e, 'NearRight','once'))
          TTL=3;
      elseif ~isempty(regexp(e, 'Right','once'))
          TTL=4;
      end
      % img type
      if ~isempty(regexp(e, 'None','once'))
          TTL=TTL+10;
      elseif ~isempty(regexp(e, 'Indoor','once'))
          TTL=TTL+20;
      elseif ~isempty(regexp(e, 'Outd0or','once'))
          TTL=TTL+30;
      end
      TTL=TTL+100;
      
  elseif strncmp(e, 'dly', 3) % || strncmp(e, 'isi', 3)
      TTL=160;
  elseif strncmp(e, 'mgs', 3)
      TTL=210;
  else
      error('unknown event %s', e)
  end
  
  % must be numbers and letters only
  if ~isempty(et)
      msg = [regexprep(e,'[^A-za-z0-9]',''), trl];
  else
      msg = '';
 end