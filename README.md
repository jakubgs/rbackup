# Description

This is a small utility I've made for the purpose of automating backups with `rsync` & `tar`.

# Usage

Define configuration in JSON format:

```json
{
    "assets": {
        "home": {
            "id": "home",
            "type": "rsync"
            "src": "/home/my_user/",
            "dest": "homes/my_user",
            "target": "remote_backup",
            "exclude": [ "Downloads", ".cache", ".local" ],
        },
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

# To Do

* More types of backups
* More custom options for `tar` and `rsync`
