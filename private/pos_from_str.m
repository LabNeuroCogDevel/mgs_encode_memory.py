function pos = pos_from_str(e)
  % Left NearLeft NearRight Rigth ->
  % -1 -.5 .5 1
  %
  if  ~isempty(regexp(e, 'Left','once'))
      pos = -1;
  else
      pos = 1;
  end
  pos = ~isempty(regexp(e, 'Near','once'))*.5*-1*pos + pos;

end