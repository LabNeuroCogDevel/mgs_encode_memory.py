function goodbye(w)
Screen('DrawText' ,w, 'Thank you!', 50, 50, [255 255 0]);
Screen('Flip', w);
RestrictKeysForKbCheck([]);
KbWait()
sca;
end