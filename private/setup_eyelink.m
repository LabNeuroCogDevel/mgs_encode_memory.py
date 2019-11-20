function el = setup_eyelink(etname, w)

    % give an indication to the participant
    DrawFormattedText(w, 'Calibrating!', 'center','center', [255 255 255])
    Screen('Flip',w);

    err = Eyelink('Initialize');
    if err
        error('failed to connect to eyetracker! did you run eyelink_setup.bash?')
    end

    % limited to a total of 9 characters
    err = Eyelink('OpenFile', etname);
    if err
        disp(err)
        error('cannot create %s on eyelink; filename limit is 8 chars?',...
            etname)
    end
 
    % below from EyelinkPictureCustomCal
    
    el=EyelinkInitDefaults(w);
    el.backgroundcolour = BlackIndex(el.window);
    el.msgfontcolour    = WhiteIndex(el.window);
    el.foregroundcolour = WhiteIndex(el.window);
    el.imgtitlecolour = WhiteIndex(el.window);
    %el.targetbeep = 0;
    el.calibrationtargetcolour= WhiteIndex(el.window);
    el.calibrationtargetsize= 1;
    el.calibrationtargetwidth=0.5;
    el.displayCalResults = 1;
    el.eyeimgsize=50;
    EyelinkUpdateDefaults(el);
    
    [width, height]=Screen('WindowSize', w);
    
    % it's location here is overridded by EyelinkDoTracker which resets it
    % with display PC coordinates
    Eyelink('command','screen_pixel_coords = %ld %ld %ld %ld', 0, 0, width-1, height-1);
    Eyelink('message', 'DISPLAY_COORDS %ld %ld %ld %ld', 0, 0, width-1, height-1);
    % set calibration type.
    %Eyelink('command', 'calibration_type = HV5');
    % you must send this command with value NO for custom calibration
    % you must also reset it to YES for subsequent experiments
    Eyelink('command', 'generate_default_targets = NO');

    

    % remote mode possible add HTARGET ( head target)
    Eyelink('command', 'file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT');
    Eyelink('command', 'file_sample_data  = LEFT,RIGHT,GAZE,HREF,AREA,GAZERES,STATUS,INPUT,HTARGET');
    % set link data (used for gaze cursor)
    Eyelink('command', 'link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,FIXUPDATE,INPUT');
    Eyelink('command', 'link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT,HTARGET');
    
    % this caues matlab to hang
    % somewhere el.callback = PsychEyelinkDispatchCallback
    % hangs on Eyelink('StartSetup',1); Eyelink('StartSetup',0) is okay
    % copied to private and modified
    fprintf('WATING FOR CALIBRATION\n');
    fprintf('push "a" on tracker when ready. "esc" here when done.');
    EyelinkDoTrackerSetup(el, 'c');
end