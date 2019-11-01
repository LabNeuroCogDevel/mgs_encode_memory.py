function event_info = read_events(modality, nruns)
    if nargin < 1
        modality = 'ieeg';
    end
    if nargin < 2
        nruns = 1;
        % TODO: implement this?! how
    end

    % find files like stims/modality/[0-9]*[0-9]/
    timedirs = dir(fullfile('stims', modality,'*'));
    is_tdir = arrayfun(@(x) ~isempty(regexp(x.name,'[0-9]*[0-9]$','start','once')), timedirs);
    if isempty(is_tdir)
        error('no stim timing information in "%s", try a differnt modality?', timedirs);
    end
    
    seeddir = arrayfun(@(x) fullfile(x.folder,x.name), timedirs, 'Un', 0);
    seeddir = Shuffle(seeddir([timedirs.isdir]' & is_tdir));
    seeddir = seeddir{1};
    [onsets, events] = read_stims(seeddir);
    
    % add more info to other events, get trial numbers
    trialnums = zeros(1,length(onsets));
    ctrial = 0;
    
    % get trial type from vgs label -- every trial must have vgs
    trial_type = regexp(events, '(?<=vgs)_.*','once','match');
    trial_type = trial_type(~cellfun(@isempty,trial_type)); % remove empty
   
    for eidx=1:length(events)
        e = events{eidx};
        % cue is start of new trial
        if strncmp(e, 'cue', 3)
            ctrial = ctrial + 1;
        end
        % add _side_image to every event
        if ~strncmp(e, 'vgs',3)
            events{eidx} = [e trial_type{ctrial}];
        end
        % set event trial number
        trialnums(eidx) = ctrial;       
    end
    
    event_info.onsets = onsets;
    event_info.events = events;
    event_info.seeddir = seeddir;
    event_info.trial = trialnums;

end