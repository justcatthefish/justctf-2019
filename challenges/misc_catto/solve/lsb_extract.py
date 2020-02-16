from PIL import Image
import sys

if(len(sys.argv) != 3):
	print("Usage: lsb_extract.py <in> <out>")
	sys.exit(-1)


f_in = sys.argv[1]
f_out = sys.argv[2]

i_in = Image.open(f_in)

width, height = i_in.size

for x in range(width):
	for y in range(height):
		r,_,_,_ = i_in.getpixel((x,y))
		if(r & 1 == 1):
			i_in.putpixel((x,y), (255,255,255))
		else:
			i_in.putpixel((x,y), (0,0,0))

i_in.save(f_out)