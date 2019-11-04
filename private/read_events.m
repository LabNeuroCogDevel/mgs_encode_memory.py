function event_info = read_events(modality, nblocks)
    if nargin < 1
        modality = 'ieeg';
    end
    if nargin < 2
        nblocks = 1;
        % TODO: implement this?! how
    end

    % find files like stims/modality/[0-9]*[0-9]/
    timedirs = dir(fullfile('stims', modality,'*'));
    is_tdir = arrayfun(@(x) ~isempty(regexp(x.name,'[0-9]*[0-9]$','start','once')), timedirs);
    if isempty(is_tdir)
        error('no stim timing information in "%s", try a differnt modality?', timedirs);
    end
    
    seeddir = arrayfun(@(x) fullfile(x.folder,x.name), timedirs, 'Un', 0);
    seeddir = seeddir([timedirs.isdir]' & is_tdir);
    ndirs = length(seeddir);
    if ndirs < nblocks
        warning('%d timing directories (%s) > requested blcoks (%d)!',...
                ndirs, modality, nblocks);
         seeddir = repmat(seeddir, 1, ceil(nblocks/ndirs));  
    end
    seeddir = Shuffle(seeddir);
    
    % naive way to concat onsets and events
    onsets =[]; events=[];
    for bn=1:nblocks
        [o, e] = read_stims(seeddir{bn});
        onsets = [onsets; o];
        events = [events; e];
    end
    
    % add more info to other events, get trial numbers
    trialnums = zeros(1,length(onsets));
    ctrial = 0;
    block = zeros(1,length(onsets));
    
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
        
        % set block number
        if eidx == 1
            cblock=1;
        elseif onsets(eidx,1) < onsets(eidx-1,1)
            cblock = block(eidx-1) +1;
        else
            cblock = block(eidx-1);
        end
        block(eidx) = cblock;
    end
    
    event_info.onsets = onsets;
    event_info.events = events;
    event_info.seeddir = seeddir;
    event_info.trial = trialnums;
    event_info.block = block;

end