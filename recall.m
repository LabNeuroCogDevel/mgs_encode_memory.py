function recall(matfile)

if nargin < 1
    [matfile, matdir] = uigetfile('*.mat');
    matfile = fullfile(matdir,matfile);
end

if isempty(matfile) || ~exist(matfile,'file')
    error('need a mgsrun matfile not %s', matfile)
end

%% parse data we gathered
mgsdata = load(matfile);
imgevent = ~cellfun(@isempty,regexp(mgsdata.event_info.events,'vgs_.*_[^N]','once'));
subjsaw = mgsdata.event_info.trial <= mgsdata.trial;

% get images that are known
imgs_seen = imgevent' & subjsaw;
known_img = mgsdata.imgs_used(1:nnz(imgs_seen));
known_name = cellfun(@(x) x.name, known_img, 'Un', 0);

% get position those images were displayed on
side = cellfun(@(e) pos_from_str(e), mgsdata.event_info.events);
side = side(imgs_seen);

%% get random images
all_imgs = list_images(mgsdata.event_info.imgset);
% exclude seen and make absolute path
for f=fieldnames(all_imgs)'
    this = all_imgs.(f{1});
    keep = ~ismember({this.name},known_name);
    all_imgs.(f{1}) = arrayfun(@(x) fullfile(x.folder,x.name), this(keep), 'Un',0);
end

% pick half from inside and half from outside
% and make half the outsides man made and half natural
% shuffle so if we overcount we don't always remove from indoor
neach = ceil(length(known_name)/2);
rand_imgs = ...
    Shuffle([all_imgs.outdoor_man(1:ceil(neach/2));
    all_imgs.outdoor_nat(1:ceil(neach/2));
    all_imgs.indoor(1:neach)])';

% undo any ceil overcounting
% N.B. known_img folder from mgs run. might be a problem if recall is on
%      different computer
known_fullpath = cellfun(@(x) fullfile(x.folder,x.name), known_img, 'Un',0);
imgs_test = Shuffle([rand_imgs(1:length(known_img)), known_fullpath]);

%% setup screen
w = mgs_setup('test');
Screen('TextColor', w, [255 255 255]); % white text
ypad=30;
xpad=-5;

%% setup keyboard
KbName('UnifyKeyNames');
% NB! order is important
% first 4 are position left to right
acceptKeys = KbName({'1!','2@','3#','4$', 'ESCAPE', 'q'});
RestrictKeysForKbCheck(acceptKeys);


%% first save
savename = regexprep('.mat$',['_recall' datestr(now(),'yyyymmddHHMMSS') '.mat'], matfile);
info=struct();
save(savename,'imgs_test', 'side', 'known_img', 'info')

%% get input
for idx=1:length(imgs_test)
    %% setup: should we know, what position
    img = imgs_test{idx};
    pos = NaN;
    isknown = 0;
    [~,bname, ext] = fileparts(img);
    knownidx = find(ismember(known_name,[bname ext]));
    if knownidx
        isknown = 1;
        pos = side(knownidx);
    end
    
    %% dispaly image
    [~, imgtype] = fileparts(fileparts(img));
    fprintf('known=%d\tpos=%.1f \t%s  \t%s\n', isknown, pos, imgtype, bname)
    
    
    tex = Screen('MakeTexture', w, imread(img));
    drawVGS(w, 0, tex, 0);
    Screen('DrawText',w, 'Did you see this image (1 no - 4 definetly)', 50, 50);
    
    [x, y] = drawVGS(w,  -1, [], 0); % dont draw but get where we would
    Screen('DrawText' ,w, 'new', x, y);
    
    [x, y] = drawVGS(w,  1, [], 0); % dont draw but get where we would
    Screen('DrawText' ,w, 'seen', x, y);
        
    flip_k = Screen('Flip',w);
    [kc_saw, kt_k] = Kb();
    
    %% display position
    if ismember(kc_saw, acceptKeys(3:4))
        Screen('DrawText' ,w, 'what position (1 left - 4 right)', 50, 50);
        drawVGS(w, 0, tex, 0);

        
        [x, y] = drawVGS(w,  -1, []);
        Screen('DrawText' ,w, '1', x+xpad, y+ypad);
        [x, y] = drawVGS(w, -.5, []);
        
        Screen('DrawText' ,w, '2', x+xpad, y+ypad);

        [x, y] = drawVGS(w,  .5, []);
        Screen('DrawText' ,w, '3', x+xpad, y+ypad);

        [x, y] = drawVGS(w,   1, []);
         Screen('DrawText' ,w, '4', x+xpad, y+ypad);


        flip_p = Screen('Flip',w);
        [kc_pos, kt_p] = Kb();
    else
        kc_pos = 0;
        flip_p = 0;
        kt_p = 0;
    end
    
    Screen('Close', tex);

    %% score
    % TODO: match python
    % seen
    % 1, 2 = didn't see | 3,4 = saw
    pushed_img = find(kc_saw == acceptKeys);
    actual_img = 1 + isknown*3; % 1 = no; 4=yes
    mostly_img = (pushed_img > 2) == isknown;
    exact_img = pushed_img == actual_img;
    
    % position
    actual_pos_key = find(pos == [-1 -.5 .5 1]);
    pushed_pos_key = find(kc_pos == acceptKeys);
    same_side = (actual_pos_key > 2) == (pushed_pos_key > 2);
    exact_pos = actual_pos_key == pushed_pos_key;

    if isfinite(pos)
        score = same_side*25 + exact_pos*50;
    else
        score = 1;
    end
    score = score + mostly_img*100 + 50*exact_img;
    
    fprintf('seen: %d\tpos: %d\tscore: %d\n', kc_saw, kc_pos, score);
    
    info(idx).img=img;
    info(idx).img=imgtype;
    info(idx).img=bname;
    info(idx).isknown=isknown;
    info(idx).pos=pos;
    info(idx).score=score;
    info(idx).kc_saw = kc_saw;
    info(idx).kc_pos = kc_pos;
    info(idx).flip_p = flip_p;
    info(idx).kt_p = kt_p;
    info(idx).kt_k = kt_k;
    info(idx).flip_k = flip_k;

    save(savename,'imgs_test', 'side', 'known_img', 'info');
    
end

% all done
goodbye(w)

end

function [kc, t] = Kb()
% get keypush. exit if esc or q pushed
% time is release time!
      t = 0;
      [~, kc, t] = KbWait([],2); % wait for release
      kc = find(kc);
      if any(ismember([KbName('ESCAPE'), KbName('q')], kc))
          kc = 0;
          sca;
          error('user escape/q exit!')
      end
      kc = kc(1);
      % time to release
      WaitSecs(.1);
end