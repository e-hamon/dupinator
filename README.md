dupinator
=========

The original dupinator.py script was created by Bill Bumgarner.

This version was created by Erwan Hamon and produces a bash script that can be reviewed and edited.

The script is used to find duplicate files, taking care to use as little CPU as possible, thus only comparing files of the same size, then checking the first kb for differences, and after that using filecmp.

```
Usage: dupinator.py [options] [dir]...

Options:
  -h, --help       show this help message and exit
  -1, --keep1      Keep files in first target directory
  -m, --move       Move duplicate files to ~/zzz instead of deleting them
  -k, --kmail      In kmail maildirs, delete unread mails first
  -R, --recursive  Visit subdirectories recursively.
  -d, --debug      Verbose output for debugging
  -v, --verbose    Verbose output but less than debug
```

Examples:

1 Keep anything in ~/mainfolder
  - `$ dupinator.py -1Rv ~/mainfolder ~/oldbackup > supdup.sh`
  - `$ bash supdup.sh`
2 I'm feeling lucky
  - `$ dupinator.py -Rv dir/to/clean | bash`

