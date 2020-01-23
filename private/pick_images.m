function imgs_used = pick_images(events, imgset)
% list all images we need for textures
% pass to make_textures

    % find indoor and outdoor images we need
    imgtype = cellfun(@(x) regexp(x,'vgs.*(Indoor|Outdoor)','match'), events, 'Un',0);
    
    files = list_images(imgset);
    % outdoor needs to be broken into manmade (_man) and natural (_nat)
    tex_needed = regexprep(vertcat(imgtype{:}),'vgs_.*_','');
    outidx = find(ismember(tex_needed,'Outdoor'));  
    outidx = Shuffle(outidx);
    imgs_used = cell(1,length(tex_needed));
    % odd random outside index pull from natural
    fi=1;
    for i=outidx(1:2:end)'
        imgs_used{i} = files.outdoor_nat(fi);
        fi=fi+1;
    end
    % even random index pull from manmade
    fi=1;
    for i=outidx(2:2:end)'
        imgs_used{i} = files.outdoor_man(fi);
        fi=fi+1;
    end
    % the rest pull from indoor
    fi=1;
    for i=setdiff(1:length(tex_needed), outidx)
        imgs_used{i} = files.indoor(fi);
        fi=fi+1;
    end
end

%!function [used, e, idx] = create()
%! d=defs();
%! event_info = read_events(d.modality, d.nblock);
%! used = pick_images(event_info.events, d.imgset);
%! e = event_info.events;
%! idx = setdiff(strmatch('vgs',e), find(~cellfun(@isempty,regexp(e,'.*None','match'))));
%!endfunction

%% correct length
%!test
%! [img, e, idx] = create();
%! assert(length(idx), length(img))

%% matches in/out (side|door)
%!test
%! [img, e, idx] = create();
%! event = cellfun(@(x) lower(regexp(x,'(In|Out)(?=door)','match'){1}), e(idx), 'Un',0);
%! fromdir = cellfun(@(x) regexp(x.folder,'(in|out)(?=side)','match'){1}, img, 'Un',0)';
%! assert(event,fromdir)

%% is random
%!test
%! d=defs();
%! event_info = read_events(d.modality, d.nblock);
%! used =  cellfun(@(x) x.name, pick_images(event_info.events, d.imgset), 'Un', 0);
%! used2 = cellfun(@(x) x.name, pick_images(event_info.events, d.imgset), 'Un', 0);
%! assert(~all(arrayfun(@(i) strcmp(used{i},used2{i}), 1:length(used))))

