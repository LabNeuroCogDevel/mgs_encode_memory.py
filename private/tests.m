
% go back one from private
cd([filepaths(mfilename('fullpath') '/..'])
subj='testme'
imgset='A'
nblock=2

savefile = resume_or_new(subj, imgset, nblock, 'n');
load(savefile, 'event_info','imgs_used','starttime', 'eventtimes', 'trial');

[w, hid, et] = mgs_setup(subj, use_et);
