#!/bin/bash

cp ../public/matryoshka.jpg 1.jpg

for i in {1..3}
do
    exiftool -b -ThumbnailImage "$i.jpg" > "$((i+1)).jpg"
done