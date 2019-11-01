function [sorted_times, sorted_events] = read_stims(path)
   % path='stims/ieeg/3479197962273054302'
   % read all inputs of a given name
   onsets=struct();
   durs=struct();
   stim_files = dir(fullfile(path,'*1D'));
   for f=stim_files'
       fname = fullfile(f.folder, f.name);
       fid = fopen(fname);
       if fid == -1
           fprintf('%s isnt readable!?\n', fname); 
       end
       stims = fscanf(fid, '%f:%f');
       
       [~,n] = fileparts(f.name);
       onsets.(n) = stims(1:2:end);
       durs.(n) = stims(2:2:end);
       fclose(fid);
       
       % sanity check
       if ~ all(diff(onsets.(n)) > 0) || ~ all(durs.(n) < 20)
           error('error reading in %s; onsets not monotonic or durs >20', fname);
       end

   end

       
   event_names = fieldnames(onsets);
   event = cellfun(@(x) repmat({x},length(onsets.(x)),1), event_names,'Un',0);
   times = cellfun(@(x) onsets.(x), event_names,'Un',0);
   d = cellfun(@(x) durs.(x), event_names,'Un',0);
   event = vertcat(event{:}); d=vertcat(d{:}); times=vertcat(times{:});
   
   timing = [times, d];
   [~, si] = sort(times);
   sorted_times = timing(si,:);
   sorted_events = event(si);

      
   if length(timing) < 10
       error('too few events (%d<10) in stim onsets "%s"!', length(timing), path);
   end
   
end