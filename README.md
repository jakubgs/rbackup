# Description

This is a small utility I've made for the purpose of automating backups with `rsync` & `tar`.

# Usage

Define configuration in JSON format, usually in `/etc/rbackup.json`:

```json
{
    "assets": {
        "home": {
            "id": "home",
            "type": "rsync",
            "src": "/home/my_user/",
            "dest": "homes/my_user",
            "target": "remote_backup",
            "exclude": [ "Downloads", ".cache", ".local" ]
        }
    }, 
    "targets": {
        "remote_backup": {
            "id": "remote_backup",
            "dest": "/mnt/backup",
            "host": "some.host.i.own",
            "user": "some_user"
        }
    }
}
```

Now simply run the backup:

```bash
$ rbackup --asset home   
2017-12-15 18:09:15,119 - INFO: Starting rsync: /home/my_user -> some_user@some.host.i.own:22:/mnt/backup/homes/my_user
2017-12-15 18:09:15,535 - INFO: Finished in: 1.42s
2017-12-15 18:09:15,535 - INFO: sent 1.22M bytes  received 11 bytes  2.45M bytes/sec
2017-12-15 18:09:15,535 - INFO: total size is 360.01M  speedup is 294.13
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
