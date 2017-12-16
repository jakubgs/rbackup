# Description [![Build Status](https://travis-ci.org/PonderingGrower/rbackup.svg?branch=master)](https://travis-ci.org/PonderingGrower/rbackup)

This is a small utility I've made for the purpose of automating backups with `rsync` & `tar`.

**WARNING:** This package is not yet stable. Use at own peril.

# Installation

Not available in PyPi yet so you have to install from GitHub:

```bash
pip install git+https://github.com/PonderingGrower/rbackup
```

Or clone it, and build it by hand:

```bash
git clone https://github.com/PonderingGrower/rbackup
cd rbackup
./setup.py test
./setup.py sdist
pip install dist/rbackup-0.1.tar.gz
```

# Usage

Define configuration in YAML format, usually in `/etc/rbackup.yaml`:

```yaml
assets:
  - id: example
    type: rsync
    src: /tmp/example
    dest: example
    target: remote_backup
    exclude: [ something, another_thing ]
targets:
  - id: remote_backup
    dest: /mnt/backup
    host: bkp.example.com
    user: userx
```

Now simply run the backup:

```bash
$ rbackup --asset example
INFO: Starting rsync: /tmp/example -> userx@bkp.example.com:/mnt/backup/example
INFO: Finished in: 6.22s
INFO: sent 20.36K bytes  received 15 bytes  3.13K bytes/sec
INFO: total size is 20.21M  speedup is 991.80
```

Or restore:

```bash
$ rbackup --asset example --restore
WARNING: Enabled RESTORE mode!
INFO: Starting rsync: userx@bkp.example.com:/mnt/backup/example -> /tmp/example
INFO: Finished in: 10.72s
INFO: sent 8.41K bytes  received 20.25M bytes  1.76M bytes/sec
INFO: total size is 20.21M  speedup is 1.00
```

# Help

```
usage: rbackup [-h] [-a ASSETS [ASSETS ...]] [-t TYPE] [-T TIMEOUT]
               [-p PID_FILE] [-l LOG_FILE] [-D] [-o] [-r] [-d] [-s] [-P] [-b]
               [-f] [-c CONFIG]

This script backups directories configred as 'assets' in the YAML config file.

Configuration can be also provided through standard input using --stdin flag..
The config is merged with the one read from the file.

Config file locations read in the following order:
* /etc/rbackup.yaml
* ~/rbackup.yaml
* ./rbackup.yaml

optional arguments:
  -h, --help            show this help message and exit
  -a ASSETS [ASSETS ...], --assets ASSETS [ASSETS ...]
                        List of assets to process.
  -t TYPE, --type TYPE  Type of backup to execute: rsync / tar
  -T TIMEOUT, --timeout TIMEOUT
                        Time after which rsync command will be stopped.
  -p PID_FILE, --pid-file PID_FILE
                        Location of the PID file.
  -l LOG_FILE, --log-file LOG_FILE
                        Location of the log file.
  -D, --dryrun          Run the code without executing the backup command.
  -o, --one-instance    Check if there is another instance running.
  -r, --restore         Instead of backing up, restore.
  -d, --debug           Enable debug logging.
  -s, --stdin           Get configuration from STDIN as well.
  -P, --print-config    Show current configuration of sources and targets.
  -b, --battery-check   Enable checking for battery power before running.
  -f, --force           When used things like running on battery are ignored.
  -c CONFIG, --config CONFIG
                        Location of YAML config file.
```

# To Do

* Unit tests
* Functional tests
* More sane restore mode
* More types of backups
* More custom options for `tar` and `rsync`
