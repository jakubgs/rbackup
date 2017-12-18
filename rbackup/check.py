import re
import sh

from rbackup import config
from rbackup.log import LOG


def ssh_works(target, timeout=1):
    host_str = '{}@{}'.format(target.user, target.host)

    ssh = sh.ssh.bake(F='/dev/null',  # ignore configuration
                      q=True,
                      l=target.user,
                      p=target.port or 22)
    ssh = ssh.bake(o='ConnectTimeout={}'.format(timeout))
    ssh = ssh.bake(o='UserKnownHostsFile=/dev/null')
    ssh = ssh.bake(o='StrictHostKeyChecking=no')
    ssh = ssh.bake(target.host)
    LOG.debug('CMD: %s', ssh)
    try:
        ssh.exit()
    except Exception as e:
        LOG.info('Host not available: %s', host_str)
        return False
    return True

def ping_works(target, min_ping=config.DEFAULT_MINIMAL_PING):
    if not target.ping or target.host == 'localhost':
        return True
    ping = sh.ping.bake(target.host, '-c1')
    LOG.debug('CMD: %s', ping)
    try:
        r = ping()
    except Exception as e:
        return False
    print(r.stdout)
    m = re.search(r'time=([^ ]*) ', r.stdout)
    print(m)
    time = float(m.group(1))
    if time > min_ping:
        LOG.warning('Ping or host too slow({}s), abandoning.'.format(ping))
        return False
    return True
