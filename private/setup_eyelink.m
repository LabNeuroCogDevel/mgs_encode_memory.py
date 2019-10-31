function setup_eyelink(etname)
    err = Eyelink('Initialize');
    if err
        error('failed to connect to eyetracker! did you run eyelink_setup.bash?')
    end

    % limited to a total of 9 characters
    err = Eyelink('OpenFile', etname);
    if err
        error('cannot create %s on eyelink; filename limit is 9 chars?',...
            etname)
    end
end