function files = list_images(imgset)
    files.indoor = Shuffle(dir(fullfile('img/', imgset, '/inside/*png')));
    files.outdoor_nat = Shuffle(dir(fullfile('img/', imgset, '/outside_nat/*png')));
    files.outdoor_man = Shuffle(dir(fullfile('img/', imgset, '/outside_man/*png')));
end