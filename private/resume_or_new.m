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
      modality = 'test';
  else
      modality = 'ieeg';
  end
  
  % define where to save and make sure we don't have anything else
  savepath = fullfile('subj_info/ieeg', subj);
  % we'll look for any files also created today
  saveprefix = [subj '_' imgset '_' datestr(now(),'yyyymmdd')];
  othermats = dir(fullfile(savepath, [saveprefix '*.mat']));
  
  % do we want to resume?
  % only relevant if we have othermats 
  resume='n';
  if ~isempty(othermats)
      warning('have other saved files in %s', fullfile(savepath, saveprefix));
      if nargin > 3
         warning('using autoconfirm option! set resume to %s', autoconfirm);
         resume = autoconfirm;
      else
         resume = input('do you want to resume? no creates new matfile (y|n): ', 's');
      end
      validatestring(resume,{'y','n'});
  end
  
  if resume == 'y'
      % load the only option
      % of if there are more than one, prompt with gui
      if length(othermats) == 1
          savefile = fullfile(othermats(1).folder, othermats(1).name);
      else
          disp(othermats);
          [m, p] = uigetfile();
          if isempty(m)
              error('failed to select a file to resume from!')
          end
          % make relative to be consistant
          savefile = fullfile(p, m);
      end
      pwdlen=length([pwd '/'])+1;
      savefile=savefile(pwdlen:end);
      load(savefile, 'event_info','imgs_used',...
                     'trial', 'eventtimes', 'starttime');
  else
     % no resume. make new savefile
     savename = [saveprefix datestr(now(),'HHMMSS')];
     savefile = fullfile(savepath, [savename '.mat']);
  end
 
  % if we haven't resumed (default), generate new set
  if ~exist('event_info', 'var')
      event_info = read_events(modality, nblock);
      event_info.imgset = imgset;
      starttime = zeros(1, nblock);
      trial = 1;
      % filenames to be used by make_textures
      imgs_used = pick_images(event_info.events, imgset);
      % stuct for storing event onset (flip) times as they happen
      eventtimes = struct();
  else
      % restart from begining of block
      trialidx = min(find(event_info.trial == trial));
      cblock = event_info.block(trialidx);
      prevtrial = trial;
      ftrial = min(event_info.trial([event_info.block] == cblock));
      ltrial = max(event_info.trial([event_info.block] == cblock));
      % we were on the last trial - go to the next block
      if ltrial == trial 
          trial = trial +1;
          if trial > max([event_info.trial])
              error('resuming for last trial, not supported!');
          end
      else
          trial = ftrial;
      end
      warning('resuming on trial %d instead of %d', trial, prevtrial);
      event_info.prev.starttime = starttime;
      event_info.prev.last_trial = prevtrial;
  end


  savedir = fileparts(savefile);
  if ~exist(savedir,'dir'), mkdir(savedir); end

  save(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');
end

%% tests for octave
% run like:
%  octave --no-gui --eval "addpath('private');addpath('t'); test resume_or_new"
%
%! %% SETUP
%!function savefile=mknew()
%! d=defs();
%! cellfun(@unlink,glob(d.globpatt));
%! savefile = resume_or_new(d.subj, d.imgset, d.nblock, 'n');
%!endfunction

%% initial test
%!test
%! savefile = mknew();
%! d = defs();
%! load(savefile, 'event_info','imgs_used','trial', 'eventtimes', 'starttime');
%! assert(trial, 1);
%! % check save file is what we wrote
%! have = glob(d.globpatt);
%! assert(length(have), 1)
%! assert(savefile, have{1})

%% again with resume
%!test
%! %% update and save for resume
%! d = defs();
%! savefile = mknew();
%! load(savefile, 'event_info','imgs_used','trial', 'eventtimes', 'starttime');
%! block2_start = event_info.trial(min(find(event_info.block==2)));
%! trial=block2_start+5;
%! save(savefile, 'event_info','imgs_used','trial', 'eventtimes', 'starttime');
%! 
%! %% resume
%! WaitSecs(1.1); % need to wait long enough to get a new savename
%! savefile = resume_or_new(d.subj, d.imgset, d.nblock, 'y');
%!
%! %% tests
%! have = glob(d.globpatt);
%! assert(length(have), 1);
%! assert(have{1}, savefile);
%! imgs_used_orig = imgs_used;
%! load(savefile, 'event_info','imgs_used','trial', 'eventtimes', 'starttime');
%! assert(trial, block2_start);
%! n=min(length(imgs_used),length(imgs_used_orig));
%! assert(all(arrayfun(@(i) strcmp(imgs_used_orig{i}.name,imgs_used{i}.name), 1:length(imgs_used))))

%% again but create a new
%!test
%! savefile=mknew();
%! load(savefile, 'imgs_used');
%! imgs_used_orig = imgs_used;
%! d = defs();
%! WaitSecs(1.1);
%! savefile = resume_or_new(d.subj, d.imgset, d.nblock, 'n');
%! have = glob(d.globpatt);
%! assert(length(have), 2)
%! assert(savefile, have{2})
%! load(savefile, 'event_info','imgs_used','trial', 'eventtimes', 'starttime');
%! % trial resets
%! assert(trial, 1);
%! % new order -- P(new==old) = 1/(90!)  ?
%! n=min(length(imgs_used),length(imgs_used_orig));
%! assert(~all(arrayfun(@(i) strcmp(imgs_used_orig{i}.name,imgs_used{i}.name), 1:n)))
