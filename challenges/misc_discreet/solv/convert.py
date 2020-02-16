import re
import os

nums = open("../public/dft.out", "rt").read()[1:-1]

sp = [x.strip() for x in nums.split(", ")]


coords = []

rgx = re.compile("((?:-)?(?:\d)+\.(?:\d)+)((?:-|\+)(?:\d)+\.(?:\d)+)")

print("[")

for s in sp:
	grp = rgx.match(s).groups()
	print("math.complex({}, {}),".format(grp[0], grp[1]))

print("]")

