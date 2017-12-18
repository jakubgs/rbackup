import os
import sh

from rbackup.log import LOG
from rbackup.execute import execute


def _log_rsync_stats(output):
    if type(output) == bytes: # pragma: no cover
        output = output.decode()
    index = output.index('Number of files')
    full_stats = output[index:]
    div = full_stats.index('sent ')
    debug_stats = full_stats[:div]
    info_stats = full_stats[div:]
    for line in debug_stats.splitlines():
        LOG.debug(line)
    for line in info_stats.splitlines():
        LOG.info(line)

def _make_full_dest(asset, target):
    full_dest = '{}/{}'.format(target.dest, asset.dest)
    if target.host:
        return '{}@{}:{}'.format(target.user, target.host, full_dest)
    else:
        return os.path.join(target.dest, asset.dest)

def _bake_rsync_for_target(asset, target, timeout=None, restore=False):
    # prepare the rsync command
    rsync = sh.rsync.bake(archive=True,
                          recursive=True,
                          update=True,
                          times=True,
                          partial=True,
                          stats=True,
                          timeout=timeout,
                          human_readable=True,
                          delete_after=True,
                          delete_excluded=True)

    # bake in additional options
    if target.port:
        rsync = rsync.bake(rsh='ssh -p {}'.format(target.port))
    if asset.opts:
        rsync = rsync.bake(asset.opts)
    if asset.exclude:
        for entry in asset.exclude:
            rsync = rsync.bake(exclude=entry)

    return rsync

def sync(asset, target, timeout, restore=False, dryrun=False):
    if asset.type == 'rsync':
        stdout = r_sync(asset, target, timeout, restore, dryrun)
    elif asset.type == 'tar':
        stdout = tar_ssh(asset, target, timeout, restore, dryrun)
    else:
        raise Exception('No backup type specified for asset: %s', asset.id)
    LOG.debug(stdout)

def r_sync(asset, target, timeout, restore=False, dryrun=False):
    dest_full = _make_full_dest(asset, target)
    rsync = _bake_rsync_for_target(asset, target, timeout, restore)

    # add main arguments, source and destination
    if restore:
        rsync = rsync.bake(dest_full, asset.src)
        LOG.info('Starting rsync: %s -> %s', dest_full, asset.src)
    else:
        rsync = rsync.bake(asset.src, dest_full)
        LOG.info('Starting rsync: %s -> %s', asset.src, dest_full)

    if dryrun:
        return

    rsync_proc = execute(rsync, timeout=timeout)
    if rsync_proc is not None:
        _log_rsync_stats(rsync_proc.stdout)
        return rsync_proc.stdout

def tar_ssh(asset, target, timeout, restore=False, dryrun=False):
    dest_full = '{}/{}.tar.gz'.format(target.dest, asset.dest)
    tar = sh.tar.bake(create=True, gzip=True, total=True,
                      to_stdout=True, warning='no-file-changed')
    for exc_pattern in asset.exclude:
        tar = tar.bake(exclude=exc_pattern)
    tar = tar.bake(asset.src, _piped=True)
    command = sh.cat.bake('> {}'.format(dest_full))
    if target.host:
        ssh = sh.ssh.bake(
            '{}@{}'.format(target.user, target.host), p=target.port)
        LOG.debug(str(command))
        command = ssh.bake(str(command))

    LOG.info('Starting sync: %s -> TarGZ -> %s@%s:%s:%s',
             asset.src, target.user, target.host, target.port, dest_full)
    if dryrun:
        return

    return execute(command, piped=tar, timeout=timeout)
