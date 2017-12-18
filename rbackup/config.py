from os import path

# order of config files to read
DEFAULT_CONFIG_FILE_ORDER = [path.join(p, 'rbackup.yaml') for p in [
    '/etc/',                 # system wide
    path.expanduser('~'),    # home
]]

# time in seconds that the ping response have to be under
DEFAULT_MINIMAL_PING = 10
# time in seconds after which backup process will be stopped
DEFAULT_TIMEOUT = 72000
