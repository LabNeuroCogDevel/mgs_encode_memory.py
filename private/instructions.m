function instructions(w)
    % start
    disp_til_key(w, 'Memory Eye Task')

    % cue
    prep_event(w, 'cue', 0);
    disp_til_key(w, 'Prep: get ready to look at a dot', 'center', 50)
    % vgs
    % TODO: add image under dot?
    prep_event(w, 'vgs_Left', 0, []);
    disp_til_key(w, 'Look: look at the dot\nRemember that spot until it disappears', 'center', 50)
    % dly
    prep_event(w, 'dly', 0);
    disp_til_key(w, 'Wait: go back to center and focus on the yellow cross\nuntil it disappears', 'center', 50)
    % mgs
    disp_til_key(w, 'Recall: look to where dot was and focus there\nuntil a new cross appears', 'center', 50)
    % fix
    prep_event(w,'fix')
    disp_til_key(w, 'Relax: wait for the blue cross to signal a new round', 'center', 50)

    msg = [...
        '1. Prep: Look at the blue cross.' ...
        ' A dot is about to appear.\n\n' ...
        '2. Look: Look at the dot inside the dot and remember that spot'...
        ' until it goes away.\n\n' ...
        '3. Wait: Look at the yellow cross in the center.\n\n' ...
        '4. Recall: When the yellow cross goes away. ' ...
        'Look back to where you saw the dot until ... \n\n' ...
        '5. Relax: Look at the white cross in the center when it comes back.\n\n'...
        'NOTE: you do not need to remember the images for this task ' ...
        'but you may be asked about them later'];
    
    disp_til_key(w, msg, 10);

    
    img = imread('img/instruction/overview.png');
    tex = Screen('MakeTexture',w, img);
    Screen('DrawTexture',w, tex);
    Screen('Flip',w);
    WaitSecs(.5);
    KbWait();
    
end