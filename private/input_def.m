function x = input_def(msg, def)
   % INPUT_DEF get input, set to 'def' if empyt
      x = input(msg);
      if isempty(x)
          x = def;
      end
end
