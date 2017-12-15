from os import path

# location of script
SCRIPT_PATH = path.dirname(path.realpath(__file__))
# order of config files to read
DEFAULT_CONFIG_FILE_ORDER = [path.join(p, 'rbackup.json') for p in [
    '/etc/',                 # system wide
    path.expanduser('~'),    # home
    path.expanduser('./'),   # local
    SCRIPT_PATH,             # script dir
]]
DEFAULT_PID_FILE = '/tmp/backup.pid'
DEFAULT_LOG_FILE = '/tmp/backup.log'

# time in seconds that the ping response have to be under
DEFAULT_MINIMAL_PING = 10
# time in seconds after which backup process will be stopped
DEFAULT_TIMEOUT = 72000
