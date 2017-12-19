# Description

[![Build Status](https://travis-ci.org/PonderingGrower/rbackup.svg?branch=master)](https://travis-ci.org/PonderingGrower/rbackup) [![codecov](https://codecov.io/gh/PonderingGrower/rbackup/branch/master/graph/badge.svg)](https://codecov.io/gh/PonderingGrower/rbackup)

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
$ rbackup save example
INFO: Starting rsync: /tmp/example -> userx@bkp.example.com:/mnt/backup/example
INFO: Finished in: 6.22s
INFO: sent 20.36K bytes  received 15 bytes  3.13K bytes/sec
INFO: total size is 20.21M  speedup is 991.80
```

Or restore:

```bash
$ rbackup restore example
WARNING: Enabled RESTORE mode!
INFO: Starting rsync: userx@bkp.example.com:/mnt/backup/example -> /tmp/example
INFO: Finished in: 10.72s
INFO: sent 8.41K bytes  received 20.25M bytes  1.76M bytes/sec
INFO: total size is 20.21M  speedup is 1.00
```

# Help

```
RBackup ver 0.1

This script backups directories configred as 'assets' in the YAML config file.

Configuration can be also provided through standard input using --stdin flag..
The config is merged with the one read from the file.

Usage:
  rbackup (save | restore) <asset>... [-c PATH] [-T SECONDS] [-t TYPE] [-p PATH]
                                      [-l PATH] [-D] [-s] [-b] [-f] [-d]
  rbackup config
  rbackup -h | --help
  rbackup --version

Options:
  -c PATH --config PATH         Location of YAML config file.  [default: /etc/rbackup.yaml,/home/sochan/rbackup.yaml]
  -T SECONDS --timeout SECONDS  Time after which rsync command will be stopped.
  -p PATH --pid PATH            Path of PID file to check for other running instances.
  -l PATH --log PATH            Path of the log file.
  -t TYPE --type TYPE           Type of backup to execute: rsync / tar
  -D --dryrun                   Run the code without executing the backup command.
  -d --debug                    Enable debug logging.
  -s --stdin                    Get configuration from STDIN as well.
  -b --battery-check            Enable checking for battery power before running.
  -f --force                    When used things like running on battery are ignored.
```

# To Do

* Functional tests
* More sane restore mode
* More types of backups
* More custom options for `tar` and `rsync`
