from PIL import Image
import sys

if(len(sys.argv) != 3):
	print("Usage: lsb_and_cat.py <in> <out>")
	sys.exit(-1)


def catmap(x,y, n):
	return ((x+y) % n, (2*x+y) % n)

def cat3map(x,y, n):
	a = x
	b = y
	for _ in range(3):
		a, b = catmap(a,b, n)

	return a,b

f_in = sys.argv[1]
f_out = sys.argv[2]

i_in = Image.open(f_in)
i_out = Image.open(f_in)

width, height = i_in.size

for x in range(width):
	for y in range(height):
		xx, yy = cat3map(x,y, width)
		r,_,_,_ = i_in.getpixel((xx,yy))
		if(r & 1 == 1):
			i_out.putpixel((x,y), (255,255,255))
		else:
			i_out.putpixel((x,y), (0,0,0))

i_out.save(f_out)