subj='mgstest';
imgset='A';
nblock=3;
use_et=0;
skip_hid=1;

% setup
cellfun(@unlink, glob('subj_info/ieeg/mgstest/mgstest_A_*'));
savefile = resume_or_new(subj, imgset, nblock, 'n');

[w, hid, et] = mgs_setup(subj, use_et, skip_hid);
load(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');
event_tex = make_textures(w, imgs_used, event_info.events);


% screne init
prep_event(w, 'fix')
starttime = Screen('Flip', w);
% go
e = event_from_info(event_info, starttime, event_tex, 1);
