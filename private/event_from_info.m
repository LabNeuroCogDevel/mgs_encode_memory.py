function e = event_from_info(event_info, starttime, event_tex, eidx)
   % get better access to event info at a given index
   % - extract at event index
   %  * from event_info: events, block, trial, onsets (Nx2: onset, dly)
   %  * from event_tex: extract texture
   % - and calculate aboslute starttime.
   e.name = event_info.events{eidx}; % cue vgs dly msg
   e.cblock = event_info.block(eidx);  % 1 - 3 (likely)
   e.trial = event_info.trial(eidx); % 1 - 24 (likely)

   % event onset time relative to start of run
   e.rel_onset = event_info.onsets(eidx,1); 
   % absolute onset -- exact time to flip
   e.onset = starttime(e.cblock) + e.rel_onset; 
   % how long it should last (also initially read from 1D)
   e.dur   = event_info.onsets(eidx,2);
   e.tex = event_tex(eidx);
   e.eidx = eidx;
end
