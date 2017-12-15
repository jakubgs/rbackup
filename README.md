# Description

This is a small utility I've made for the purpose of automating backups with `rsync` & `tar`.

# Installation

**TODO**

# Usage

Define configuration in JSON format, usually in `/etc/rbackup.json`:

```json
{
    "assets": {
        "example": {
            "id": "example",
            "type": "rsync",
            "src": "/tmp/example",
            "dest": "example",
            "target": "remote_backup",
            "exclude": [ "Downloads", ".cache", ".local" ]
        }
    }, 
    "targets": {
        "remote_backup": {
            "id": "remote_backup",
            "dest": "/mnt/backup",
            "host": "bkp.example.com",
            "user": "userx"
        }
    }
}
```

Now simply run the backup:

```bash
$ rbackup --asset example
2017-12-15 18:09:15,119 - INFO: Starting rsync: /tmp/example -> userx@bkp.example.com:/mnt/backup/example
2017-12-15 20:49:03,986 - INFO: Finished in: 6.22s
2017-12-15 20:49:03,987 - INFO: sent 20.36K bytes  received 15 bytes  3.13K bytes/sec
2017-12-15 20:49:03,987 - INFO: total size is 20.21M  speedup is 991.80
```

Or restore:

```bash
$ rbackup --asset example --restore
2017-12-15 20:49:24,590 - WARNING: Enabled RESTORE mode!
2017-12-15 20:49:30,518 - INFO: Starting rsync: userx@bkp.example.com:/mnt/backup/example -> /tmp/example
2017-12-15 20:49:41,237 - INFO: Finished in: 10.72s
2017-12-15 20:49:41,237 - INFO: sent 8.41K bytes  received 20.25M bytes  1.76M bytes/sec
2017-12-15 20:49:41,238 - INFO: total size is 20.21M  speedup is 1.00
```

# Help

```
usage: script.py [-h] [-a ASSETS [ASSETS ...]] [-t TYPE] [-T TIMEOUT]
                 [-p PID_FILE] [-l LOG_FILE] [-D] [-o] [-r] [-d] [-s] [-P]
                 [-b] [-f] [-c CONFIG]

This script backups directories configred as 'assets' in the JSON config file.

Configuration can be also provided through standard input using --stdin flag..
The config is merged with the one read from the file.

Config file locations read in the following order:
* /etc/rbackup.json
* `~/.rbackup.json
* ./rbackup.json

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
                        Location of JSON config file.
```

# To Do

* More types of backups
* More custom options for `tar` and `rsync`
