#!/usr/bin/env python3
# https://stackoverflow.com/questions/890051/how-do-i-generate-circular-thumbnails-with-pil
import PIL, PIL.ImageDraw, PIL.ImageOps
import numpy as np
import os, os.path, glob, re, sys

from SUN.iminfo import imginfo_
rgb = np.array([[1,0,0],[0,1,0],[0,0,1]])*255


def make_circle(imfile, radius=225):
    # read in image
    im = PIL.Image.open(imfile)

    scale_by = max([radius/float(x) for x in im.size])

    newsize = [int(y * scale_by) for y in im.size]
    new_left = [int(float(x-radius)/2) for x in newsize]

    # we want all images to be the same size
    # and centered
    im = im.resize(newsize)
    im = im.crop(new_left + [x + radius for x in new_left])

    # make black mask of image
    mask = PIL.Image.new('L', im.size, 0)

    # create a circle to draw
    # circlexy = zip((0, 0), im.size)
    draw = PIL.ImageDraw.Draw(mask)

    # draw circle white on to black mask
    draw.ellipse([(0, 0), (radius, radius)], fill=255)
    # black to alpha
    im.putalpha(mask)

    return(im)

    # mask.show()
    # im.save('test.png')
    # im.show()


if __name__ == "__main__":
    if not os.path.exists('img_circle'):
        os.mkdir('img_circle')

    if len(sys.argv) < 2:
        # args = 'img/*png'
        print("give me an image or glob!")
        sys.exit(1)
    else:
        args = sys.argv[1:]

    for patt in args:
        for imgfile in glob.glob(patt):
            print(imgfile)
            outname = re.sub('.jpe?g$', '.png', os.path.basename(imgfile))
            outfile = os.path.join('SUN/circles/', outname)
            if os.path.isfile(outfile):
                continue
            im_alpha = make_circle(imgfile)
            im_alpha.save(outfile)

            # get some info
            i = imginfo_(np.asarray(im_alpha.convert('RGB')), rgb)
            print("\t%s" % i)
            np.savetxt(outfile.replace('.png', '.txt'), i, newline=' ')

            print("\t%s" % outfile)
