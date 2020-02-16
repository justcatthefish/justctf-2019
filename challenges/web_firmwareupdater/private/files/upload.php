<html>
  <head>
<link href="https://fonts.googleapis.com/css?family=Waiting+for+the+Sunrise" rel="stylesheet" type="text/css"/>
    <style>
      body {
        font-family: 'Waiting for the Sunrise', serif;
        font-size: 20px;
      }
    </style>
  </head>
  <body>
    <div>Info!<br>

<?php
$target_dir   = "uploads/";
$target_file  = $target_dir . basename(md5($_SERVER['REMOTE_ADDR'])) . ".zip";
$namefile     = basename($_FILES["fileToUpload"]["name"]);
$uploadOk     = 1;
$fileType     = strtolower(pathinfo($namefile, PATHINFO_EXTENSION));
$pathToReadme = $target_dir . basename(md5($_SERVER['REMOTE_ADDR'])) . '/README.md';

if ($_FILES["fileToUpload"]["size"] > 50000) {
    echo "<p>Sorry, your file is too large.</p>";
    $uploadOk = 0;
}

if ($fileType != "zip") {
    echo "Sorryyy, only ZIP files are allowed. " . htmlspecialchars(basename($_FILES["fileToUpload"]["name"]));
    $uploadOk = 0;
}

if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        echo "<b>The file " . htmlspecialchars($namefile) . " has been uploaded.</b>";

        $output = shell_exec('ls -lh | awk \'{print $9, $5} \' ; unzip -o -d uploads/' . basename(md5($_SERVER['REMOTE_ADDR'])) . ' ' . $target_file . ' README.md');
        echo "<div><pre><p style=\"font-size:13px\">$output</p></pre></div>";

        if (file_exists($pathToReadme)) {
            $output2 = shell_exec('cat uploads/' . basename(md5($_SERVER['REMOTE_ADDR'])) . '/README.md');
            echo '<br>Let\'s look what do we have in README!<br> $ cat ' . $pathToReadme;
            echo '<p>' . htmlspecialchars($output2) . '</p>';

            $dir         = '/var/www/html';
            $leave_files = array('example_firmware.zip', 'index.html', 'upload.php', 'uploads');

            foreach (glob("$dir/*") as $file) {
                if (!in_array(basename($file), $leave_files)) {
                    unlink($file);
                }

            }
            // delete zip file
            unlink($target_file);

            // delete uploaded file/directory
            shell_exec('rm -rf ' . $target_dir . basename(md5($_SERVER['REMOTE_ADDR'])));

        } else {
            echo 'Fail with Readme file!';
        }
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}

?>
</div>
</body>
</html>