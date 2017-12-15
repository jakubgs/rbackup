#!/usr/bin/env python2.7
import os
import re
import sys
import time
import json
import glob
import signal
import socket
import select
import atexit
import logging
import argparse
from getpass import getuser
try:
    import sh
except ImportError:
    print 'Failed to import module "sh". Please install it.'
    sys.exit(1)


# location of script
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
# order of config files to read
DEFAULT_CONFIG_FILE_ORDER = [
    '/etc/rbackup.json',                        # system wide
    os.path.expanduser('~'),                    # home
    os.path.expanduser('./'),                   # local
    os.path.join(SCRIPT_PATH, 'rbackup.json'),  # script dir
]
DEFAULT_PID_FILE = '/tmp/backup.pid'
DEFAULT_LOG_FILE = '/tmp/backup.log'

# time in seconds that the ping response have to be under
DEFAULT_MINIMAL_PING = 10
# time in seconds after which backup process will be stopped
DEFAULT_TIMEOUT = 72000

HELP_MESSAGE = """
This script backups directories configred as 'assets' in the JSON config file.

Configuration can be also provided through standard input using --stdin flag..
The config is merged with the one read from the file.

Config file locations read in the following order:
* {}
""".format('\n* '.join(DEFAULT_CONFIG_FILE_ORDER))


class TimeoutException(Exception):
    pass


def exit_handler():
    os.remove(DEFAULT_PID_FILE)


def signal_handler(signum, frame):
    raise TimeoutException('Timed out!')


class Asset(object):

    def __init__(self, id, target, src, type=None, dest='', opts=[], exclude=[]):
        self.id = id
        self.target = target
        self.src = src
        self.type = type or 'rsync'
        self.dest = dest or ''
        self.opts = opts
        self.exclude = exclude

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('id'),
                data.get('target'),
                data.get('src'),
                type=data.get('type'),
                dest=data.get('dest'),
                opts=data.get('opts'),
                exclude=data.get('exclude'),
        )


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

    def _ping_check(self, min_ping=DEFAULT_MINIMAL_PING):
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


def on_battery():
    for bat_stat_file in glob.glob('/sys/class/power_supply/BAT*/status'):
        with open(bat_stat_file) as f:
            if f.read().rstrip() == 'Discharging':
                return True


def proc_exists(pid):
    try:
        os.kill(pid, 0)
    except Exception as e:
        return False
    return True


def setup_logging(log_file, debug):
    FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
    logging.basicConfig(format=FORMAT)

    log = logging.getLogger('backup')
    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    fhandler = logging.FileHandler(log_file)
    fhandler.setFormatter(logging.Formatter(FORMAT))
    log.addHandler(fhandler)
    return log


def check_process(pid_file):
    if os.path.isfile(pid_file):
        pid = None
        with open(pid_file, 'r') as f:
            pid = f.read()
        if proc_exists(pid):
            return True, True
        else:
            return True, False

    else:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid())[:-1])
        return False, False


def verify_process_is_alone(pid_file):
    atexit.register(exit_handler)
    file_is, process_is = check_process(pid_file)
    if file_is and process_is:
        log.warning(
            'Process already in progress: {} ({})'.format(pid, pid_file))
        sys.exit(0)
    elif file_is and not process_is:
        log.warning('Pid file process is dead: {} ({})'.format(pid, pid_file))
        if args.force:
            log.warning('Removing: {}'.format(pid_file))
            exit_handler()
        else:
            sys.exit(0)


def read_config_file(config_files):
    for config_file in config_files:
        try:
            with open(config_file, 'r') as f:
                LOG.debug('Reading config from: %s', config_file)
                return json.load(f)
        except IOError as e:
            continue
    LOG.error('No config file found!')
    sys.exit(1)


def file_has_input(file):
    r, w, x = select.select([file], [], [], 0)
    if r:
        return True
    else:
        return False


def read_config_stdin():
    if not sys.stdin.isatty() and file_has_input(sys.stdin):
        LOG.warning('Reading config from STDIN...')
        try:
            return json.load(sys.stdin)
        except ValueError as e:
            return {}
    return {}


def read_config(config_files=DEFAULT_CONFIG_FILE_ORDER, stdin=False):
    config = {}
    config.update(read_config_file(config_files))
    if stdin:
        config.update(read_config_stdin())
    return config


def create_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=HELP_MESSAGE)

    parser.add_argument(
        "-a", "--assets", nargs='+', type=str, default=DEFAULT_PID_FILE,
                        help="List of assets to process.")
    parser.add_argument("-t", "--type", type=str,
                        help="Type of backup to execute: rsync / tar")
    parser.add_argument("-T", "--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="Time after which rsync command will be stopped.")
    parser.add_argument("-p", "--pid-file", type=str, default=DEFAULT_PID_FILE,
                        help="Location of the PID file.")
    parser.add_argument("-l", "--log-file", type=str, default=DEFAULT_LOG_FILE,
                        help="Location of the log file.")
    parser.add_argument("-D", "--dryrun", action='store_true',
                        help="Run the code without executing the backup command.")
    parser.add_argument("-o", "--one-instance", action='store_true',
                        help="Check if there is another instance running.")
    parser.add_argument("-r", "--restore", action='store_true',
                        help="Instead of backing up, restore.")
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Enable debug logging.")
    parser.add_argument("-s", "--stdin", action='store_true',
                        help="Get configuration from STDIN as well.")
    parser.add_argument("-b", "--battery-check", action='store_true',
                        help="Enable checking for battery power before running.")
    parser.add_argument("-f", "--force", action='store_true',
                        help="When used things like running on battery are ignored.")
    parser.add_argument("-c", "--config", type=str,
                        default=','.join(DEFAULT_CONFIG_FILE_ORDER),
                        help="Location of JSON config file.")
    return parser.parse_args()


def main():
    opts = create_arguments()
    global LOG
    LOG = setup_logging(opts.log_file, opts.debug)
    conf = read_config(opts.config.split(','), opts.stdin)

    if opts.one_instance:
        verify_process_is_alone(opts.pid_file)

    if opts.battery_check and not opts.force and on_battery():
        LOG.warning('System running on battery. Aborting.')
        sys.exit(0)

    if opts.restore:
        LOG.warning('Enabled RESTORE mode!')

    targets = dict()
    for target in conf['targets'].itervalues():
        targets[target['id']] = Target.from_dict(target)

    assets = conf['assets']
    if opts.assets:
        assets = {k: v for k, v in conf['assets'].iteritems()
                  if k in opts.assets}
    for asset_dict in assets.itervalues():
        asset = Asset.from_dict(asset_dict)
        target = targets.get(asset.target)

        if target is None:
            LOG.error(
                'Invalid target for asset %s: %s', asset.id, asset.target)
            continue
        if not target.available() and not opts.force:
            LOG.error('Skipping asset: %s', asset.id)
            continue

        # overrride type with options
        if opts.type:
            asset.type = opts.type

        target.sync(asset, opts.timeout, opts.restore, opts.dryrun)

if __name__ == "__main__":
    main()
