function pushtime = disp_til_key(w, msg, xpos)
      if nargin < 3
          xpos = 'center';
      end
      
      DrawFormattedText(w, msg, xpos,'center',[255 255 255]) 
      flip = Screen('Flip',w);
      fprintf('Waiting for anykey to continue @ %.2f+.3', flip)
      WaitSecs(.3);
      pushtime = KbWait();
end