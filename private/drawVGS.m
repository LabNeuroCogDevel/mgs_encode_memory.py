function drawVGS(w, pos, tex)
  dotsize = 20; % radius of 10 in python
  % tex = Screen('MakeTexture', w, imread('img/A/inside/sun_aaloiwdypreqzwnn.png'));
  
  [w_wd, w_hgt]=Screen('WindowSize', w);

  % images are 255, 255
  imgdim = [255 255]; % todo pull from actual tex?
  img_rad = imgdim(1)/2; 
  
  % calc position as if range is -w/2 to w/2
  % a la python code
  
  wmax = w_wd/2; % 400 on 800px screen
  
  % make sure image is on the screen
  hpos = pos * wmax; % -400 if pos=Left
  if hpos - img_rad < -1*wmax
      hpos = img_rad - wmax;
  elseif hpos + img_rad > wmax
      hpos = wmax - img_rad;
  end
  % back to range = 0 to width
  hpos = hpos + wmax;
  
  if tex
      imgrect = [0 0 imgdim];
      rect=CenterRectOnPoint(imgrect, hpos, w_hgt/2);
      Screen('DrawTexture',w, tex, imgrect, rect);
  end
  
  % yellow dot on top
  rect=CenterRectOnPoint([0 0 dotsize dotsize], hpos, w_hgt/2);
  Screen( 'FillOval', w, [255 255 0],  rect);
end

function scl = imgrat(screenndim, imgdim, scaleby)
    scl = screendim * scaleby/imgdim;
end