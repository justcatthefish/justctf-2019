# taken from https://github.com/zhanxw/cat

import sys
from PIL import Image
from numpy import *


if(len(sys.argv) != 4):
	print("Usage: catmap.py <input> <output> <steps>")
	sys.exit(-1)

f_in = sys.argv[1];
f_out = sys.argv[2];
steps = int(sys.argv[3]);


# load image
im = array(Image.open(f_in))
N = im.shape[0]

# create x and y components of Arnold's cat mapping
x,y = meshgrid(range(N),range(N))
xmap = (2*x+y) % N
ymap = (x+y) % N

for i in range(steps):
	im = im[xmap,ymap]

result = Image.fromarray(im)
result.save(f_out)
