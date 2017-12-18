import logging
from pytest import mark
from mock import patch, Mock

from rbackup.asset import Asset
from rbackup.target import Target
from rbackup import sync

RSYNC_OUTPUT = [
    'Number of files: 53,051 (reg: 45,676, dir: 7,246, link: 129)',
    'Number of created files: 0',
    'Number of deleted files: 0',
    'Number of regular files transferred: 13',
    'Total file size: 360.77M bytes',
    'Total transferred file size: 421.69K bytes',
    'Literal data: 421.69K bytes',
    'Matched data: 0 bytes',
    'File list size: 1.18M',
    'File list generation time: 1.024 seconds',
    'File list transfer time: 0.000 seconds',
    'Total bytes sent: 1.67M',
    'Total bytes received: 283',
    'sent 1.67M bytes  received 283 bytes  1.11M bytes/sec',
    'total size is 360.77M  speedup is 216.61',
]

def test__log_rsync_stats(caplog):
    caplog.set_level(logging.DEBUG)
    sync._log_rsync_stats('\n'.join(RSYNC_OUTPUT))
    for rec in caplog.records:
        print(rec.levelname, rec.msg)
        if rec.levelno == logging.INFO:
            assert 'sent' in rec.msg or 'total size' in rec.msg
        else:
            assert rec.msg in RSYNC_OUTPUT
