function prep_event(w, e, varargin)
  if strncmp(e, 'fix', 3)
      drawCross(w, [255 255 255]) % white
  elseif strncmp(e, 'cue', 3)
      drawCross(w, [0 0 255]) % blue
  elseif strncmp(e, 'vgs', 3)
      % -1 -.5 .5 1
      pos = pos_from_str(e);
      % img_tex = varargin{1};
      % TODO: show image at correct pos
  elseif strncmp(e, 'mgs', 3)
      % mempty screen
  elseif strncmp(e, 'dly', 3) || strncmp(e, 'isi', 3)
      drawCross(w, [255 255 0]) % yellow
  end
end

function pos = pos_from_str(e)
  % -1 -.5 .5 1
  pos = ~isempty(regexp(e, 'Near'))*.5 + ~isempty(regexp(e, 'Left'))*-1;
  if pos >=1; pos= pos-.5; end
end