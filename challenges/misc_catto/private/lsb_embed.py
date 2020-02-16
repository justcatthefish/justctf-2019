from PIL import Image
import sys

if(len(sys.argv) != 4):
	print("Usage: lsb_emed.py <carrier> <mono input> <output>")
	sys.exit(-1)


f_carrier = sys.argv[1]
f_data = sys.argv[2]
f_out = sys.argv[3]

i_carrier = Image.open(f_carrier)
i_data = Image.open(f_data)

width, height = i_carrier.size

for x in range(width):
	for y in range(height):
		r,g,b, _ = i_carrier.getpixel((x,y))
		r = (r & ~1) | (i_data.getpixel((x,y))[0] == 0)
		i_carrier.putpixel((x,y), (r,g,b))

i_carrier.save(f_out)