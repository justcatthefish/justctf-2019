#!/bin/bash

for i in {1..3}
do
    exiftool "-thumbnailimage<=$((5-i)).jpg" "$((4-i)).jpg"
done

cp 1.jpg ../public/matryoshka.jpg