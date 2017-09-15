#!/usr/bin/env python3
# https://stackoverflow.com/questions/890051/how-do-i-generate-circular-thumbnails-with-pil
import PIL, PIL.ImageDraw, PIL.ImageOps
import os,os.path, glob

def make_circle(imfile):
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

if not os.path.exists('img_circle'): os.mkdir('img_circle')
for imgfile in glob.glob('img/*png'):
    im_alpha= make_circle(imgfile)
    outname=os.path.basename(imgfile)
    outfile=os.path.join('img_circle',outname)
    print(imgfile)
    im_alpha.save(outfile)
     
