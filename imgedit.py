#!/usr/bin/env python3
# https://stackoverflow.com/questions/890051/how-do-i-generate-circular-thumbnails-with-pil
import PIL, PIL.ImageDraw, PIL.ImageOps
import os,os.path, glob, re

def make_circle(imfile,circlesize=[(0,0),(225,225)]):
  # read in image
  im = PIL.Image.open(imfile)
  # we want all images to be the same size
  im=im.resize((225,225))
  # make black mask of image
  mask=PIL.Image.new('L',im.size,0)

  
  # create a circle to draw
  draw=PIL.ImageDraw.Draw(mask)
  circlexy=zip((0,0), im.size) 
  
  # draw circle white on to black mask
  draw.ellipse( circlesize,fill=255)
  # black to alpha
  im.putalpha(mask)
  return(im)

  #mask.show()
  #im.save('test.png')
  #im.show()

if __name__ == "__main__":
 import sys
 if not os.path.exists('img_circle'): os.mkdir('img_circle')

 if len(sys.argv) != 2:
     patt='img/*png'
 else:
     patt=sys.argv[1]
     
 for imgfile in glob.glob(patt):
     im_alpha= make_circle(imgfile)
     outname=re.sub('.jpe?g$','.png',os.path.basename(imgfile))
     outfile=os.path.join('img_circle',outname)
     print(imgfile)
     im_alpha.save(outfile)
     
