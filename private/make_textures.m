function [tex_all, texf] = make_textures(w, events, imgset)
% events is a cell array of chars
% we care about the vgs ones -- we want a random image from indoor/outdoor
    imgtype = cellfun(@(x) regexp(x,'vgs.*(Indoor|Outdoor)','match'), events, 'Un',0);
    
    files = list_images(imgset);
    % outdoor needs to be broken into manmade (_man) and natural (_nat)
    tex_needed = regexprep(vertcat(imgtype{:}),'vgs_.*_','');
    outidx = find(ismember(tex_needed,'Outdoor'));  
    outidx = Shuffle(outidx);
    texf = cell(1,length(tex_needed));
    % odd random outside index pull from natural
    fi=1;
    for i=outidx(1:2:end)'
        texf{i} = files.outdoor_nat(fi);
        fi=fi+1;
    end
    % even random index pull from manmade
    fi=1;
    for i=outidx(2:2:end)'
        texf{i} = files.outdoor_man(fi);
        fi=fi+1;
    end
    % the rest pull from indoor
    fi=1;
    for i=setdiff(1:length(tex_needed), outidx)
        texf{i} = files.indoor(fi);
        fi=fi+1;
    end
    % make dir struct into texture
    tex = cellfun(@(f) Screen('MakeTexture',w,imread(fullfile(f.folder,f.name))), texf);
    % put a bunch of no textures everywhere
    tex_all = zeros(1,length(imgtype));
    % add actually textures where we need them
    tex_all(~cellfun(@isempty,imgtype)) = tex;
end