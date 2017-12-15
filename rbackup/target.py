import os
import sys
import time
import signal
from getpass import getuser

from log import LOG
import config as conf
try:
    import sh
except ImportError:
    print('Failed to import module "sh". Please install it.')
    sys.exit(1)


class TimeoutException(Exception):
    pass

def signal_handler(signum, frame):
    raise TimeoutException('Timed out!')


class Target(object):

    def __init__(self, id, dest, user=getuser(), host='localhost', port=22, ping=False):
        self.id = id
        assert self.id is not None
        self.dest = dest
        assert self.dest is not None
        self.user = user
        self.host = host
        self.port = port
        self.ping = ping

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('id'),
                data.get('dest'),
                user=data.get('user'),
                host=data.get('host'),
                port=data.get('port'),
                ping=data.get('ping'),
        )

    def available(self):
        return self._ping_check() and self._ssh_check()

    def _ssh_check(self, timeout=1):
        if not self.host:
            return True
        host_str = '{}@{}'.format(self.user, self.host)

        ssh = sh.ssh.bake(F='/dev/null',  # ignore configuration
                          q=True,
                          l=self.user,
                          p=self.port or 22)
        ssh = ssh.bake(o='ConnectTimeout={}'.format(timeout))
        ssh = ssh.bake(o='UserKnownHostsFile=/dev/null')
        ssh = ssh.bake(o='StrictHostKeyChecking=no')
        ssh = ssh.bake(self.host)
        LOG.debug('CMD: %s', ssh)
        try:
            ssh.exit()
        except Exception as e:
            LOG.info('Host not available: %s', host_str)
            return False
        return True

    def _ping_check(self, min_ping=conf.DEFAULT_MINIMAL_PING):
        if not self.ping:
            return True
        ping = sh.ping.bake(self.host, '-c1')
        LOG.debug('CMD: %s', ping)
        try:
            r = ping()
        except Exception as e:
            return False
        m = re.search(r'time=([^ ]*) ', r.stdout)
        time = float(m.group(1))
        if time > min_ping:
            LOG.warning('Ping or host too slow({}s), abandoning.'.format(ping))
            return False
        return True

    def _log_rsync_stats(self, output):
        index = output.index('Number of files')
        full_stats = output[index:]
        div = full_stats.index('sent ')
        debug_stats = full_stats[:div]
        info_stats = full_stats[div:]
        for line in debug_stats.splitlines():
            LOG.debug(line)
        for line in info_stats.splitlines():
            LOG.info(line)

    def _make_full_dest(self, asset):
        if self.host:
            return '{}@{}:{}'.format(self.user, self.host, dest_full)
        else:
            return os.path.join(self.dest, asset.dest)

    def _bake_rsync_for_target(self, asset, restore=False):
        dest_full = self._make_full_dest(asset)

        # prepare the rsync command
        rsync = sh.rsync.bake(archive=True,
                              recursive=True,
                              update=True,
                              times=True,
                              partial=True,
                              stats=True,
                              human_readable=True,
                              delete_after=True,
                              delete_excluded=True)

        # bake in additional options
        if self.port:
            rsync = rsync.bake(port=self.port)
        if asset.opts:
            rsync = rsync.bake(asset.opts)
        if asset.exclude:
            for entry in asset.exclude:
                rsync = rsync.bake(exclude=entry)

        # add main arguments, source and destination
        if restore:
            rsync = rsync.bake(dest_full, asset.src)
        else:
            rsync = rsync.bake(asset.src, dest_full)
        return rsync, dest_full

    def execute(self, command, timeout):
        LOG.debug('CMD: %s', command)

        # prepare timer to kill command if it runs too long
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(timeout)
        LOG.debug('Command timeout: %s', timeout)
        try:
            start = time.time()
            proc = command(_bg=True)
            proc.wait()
            end = time.time()
        except KeyboardInterrupt as e:
            LOG.warning('Command stopped by KeyboardInterrupt!')
            proc.terminate()
            proc.kill()
            LOG.warning('Killed process: {}'.format(proc.pid))
            return None
        except TimeoutException as e:
            proc.terminate()
            proc.kill()
            LOG.error('Command timed out after {} seconds!'.format(timeout))
            return None
        except sh.ErrorReturnCode as e:
            LOG.error('Failed to execute command: %s', command)
            LOG.error('Output:\n{}'.format(
                e.stderr or getattr(proc, 'stderr')))
            return None
        LOG.info('Finished in: {}s'.format(round(end - start, 2)))
        return proc

    def sync(self, asset, timeout, restore=False, dryrun=False):
        if asset.type == 'rsync':
            LOG.debug(self.rsync(asset, timeout, restore, dryrun))
        elif asset.type == 'tar':
            LOG.debug(self.tar_ssh(asset, timeout, restore, dryrun))
        else:
            raise Exception('No backup type specified for asset: %s', asset.id)

    def rsync(self, asset, timeout, restore=False, dryrun=False):
        rsync_full, dest_full = self._bake_rsync_for_target(asset,
                                                            restore=restore)

        LOG.info('Starting rsync: %s -> %s',
                 asset.src, dest_full)
        if dryrun:
            return

        rsync_proc = self.execute(rsync_full, timeout)
        if rsync_proc is not None:
            self._log_rsync_stats(rsync_proc.stdout)
            return rsync_proc.stdout

    def tar_ssh(self, asset, timeout, restore=False, dryrun=False):
        dest_full = '{}/{}.tar.gz'.format(self.dest, asset.dest)
        tar = sh.tar.bake(create=True, gzip=True, total=True,
                          to_stdout=True, warning='no-file-changed')
        for exc_pattern in asset.exclude:
            tar = tar.bake(exclude=exc_pattern)
        tar = tar.bake(asset.src)
        cat = sh.cat.bake('> {}'.format(dest_full))
        if self.host:
            ssh = sh.ssh.bake(
                '{}@{}'.format(self.user, self.host), p=self.port)
            LOG.debug(str(cat))
            ssh_pipe = ssh.bake(str(cat))
            command = ssh_pipe.bake(tar, _piped=True)
        else:
            command = cat.bake(tar, _piped=True)

        LOG.info('Starting sync: %s -> TarGZ -> %s@%s:%s:%s',
                 asset.src, self.user, self.host, self.port, dest_full)
        if dryrun:
            return

        return self.execute(command, timeout)