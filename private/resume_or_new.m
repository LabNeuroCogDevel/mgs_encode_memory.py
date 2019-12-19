function savefile = resume_or_new(subj, imgset, nblock, autoconfirm)
  % return what file we should save outputs. initilize some settings if they do not exist
  % * `subject` can be any string
  % * `imgset` should be 'A' 'B' or 'C'
  % * `nblock` is the total number of blocks (runs) - probably 3
  % * `autoconfirm` should be 'y' or 'n'
  %
  % populates and saves like
  %   save(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');
  % TODO: eventtimes not initilzed if not resume?

  if strcmp(subj,'test')
      modality='test';
  else
      modality = 'ieeg';
  end
  
  % define where to save and make sure we don't have anything else
  savepath = fullfile('subj_info/ieeg', subj);
  % we'll look for any files also created today
  saveprefix = [subj '_' imgset '_' datestr(now(),'yyyymmdd')];
  othermats = dir(fullfile(savepath, [saveprefix '*.mat']));
  
  % are there other files we could load from?
  if ~isempty(othermats)
      warnings('have other safe files in %s', fullfile(savepath, saveprefix));
      if nargin > 3
         resume = autoconfirm
      else
         resume = input('do you want to resume? no creates new matfile (y|n): ',s);
      end
      validatestring(resume,{'y','n'})
      if length(othermats) == 1
          savefile = fullfile(othermats(1).folder, othermats(1).name);
      else
          disp(othermats)
          [m, p] = uigetfile();
          if isempty(m)
              error('failed to select a file to resume from!')
          end
          savefile = fullfile(p, m);
      end
      load(savefile, 'event_info','imgs_used',...
                     'trial', 'eventtimes', 'starttimes')
  else
    % no other files -- save
    savename = [saveprefix datestr(now(),'HHMMSS')];
    savefile = fullfile(savepath, [savename '.mat']);
  end
    
  % if we haven't resumed (default), generate new set
  if ~exist('event_info', 'var')
      event_info = read_events(modality, nblock);
      event_info.imgset = imgset;
      starttime = zeros(1, nblock);
      trial = 1;
      % stuct for storing event onset (flip) times as they happen
      eventtimes = struct();
  else
      % restart from begining of block
      cblock = event_info.block(trial);
      prevtrial = trial;
      ftrial = min(event_info.trial([event_info.block] == cblock));
      ltrial = max(event_info.trial([event_info.block] == cblock));
      % we were on the last trial - go to the next block
      if ltrial == trial 
          trial = trial +1;
          if trial > max([event_info.trial])
              error('resuming for last trial, not supported!')
          end
      else
          trial = ftrial;
      end
      warning('resuming on trial %d instead of %d', trial, prevtrial)
      event_info.prev.starttimes = starttimes;
      event_info.prev.last_trial = prevtrial;
  end
  
    
  savedir = fileparts(savefile);
  if ~exist(savedir,'dir'), mkdir(savedir); end
  
  save(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');
  
