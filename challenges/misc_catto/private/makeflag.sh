python3 ./catmap.py flag.png flag_scrambled.png 297 # scramble the flag image, 297 steps
# python3 ./catmap.py flag_scrambled.png flag_descrambled.png  3 # descramble the flag image, 3 steps
# compare -verbose -metric AE flag.png flag_descrambled.png /dev/null
python3 lsb_embed.py cat.png flag_scrambled.png cat_with_flag.png
echo "(x,y)->(2*x+y,x+y) MOD N" | cat cat_with_flag.png - > ../public/catto.png