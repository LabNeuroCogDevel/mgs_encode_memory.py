function tex_all = make_textures(w, imgs_used, events)
% read images from list_images as textures
% we care about the vgs ones -- we want a random image from indoor/outdoor
    imgtype = cellfun(@(x) regexp(x,'vgs.*(Indoor|Outdoor)','match'), events, 'Un', 0);

    % make dir struct into texture
    tex = cellfun(@(f) ...
            Screen('MakeTexture',w, imread(fullfile(f.folder,f.name))), imgs_used);
    
    % put a bunch of no textures everywhere
    tex_all = zeros(1,length(imgtype));
    % add actually textures where we need them
    tex_all(~cellfun(@isempty,imgtype)) = tex;
end
