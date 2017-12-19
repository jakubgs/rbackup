import sys
import argparse
from docopt import docopt

from rbackup import __version__
from rbackup import utils, config
from rbackup.log import setup_logging
from rbackup.sync import sync

HELP = """RBackup ver {version}

This script backups directories configred as 'assets' in the YAML config file.

Configuration can be also provided through standard input using --stdin flag..
The config is merged with the one read from the file.

Usage:
  rbackup (save | restore) <asset>... [-c PATH] [-T SECONDS] [-t TYPE] [-p PATH]
                                      [-l PATH] [-D] [-s] [-b] [-f] [-d]
  rbackup config
  rbackup -h | --help
  rbackup --version

Options:
  -c PATH --config PATH         Location of YAML config file.  [default: {config}]
  -T SECONDS --timeout SECONDS  Time after which rsync command will be stopped.
  -p PATH --pid PATH            Path of PID file to check for other running instances.
  -l PATH --log PATH            Path of the log file.
  -t TYPE --type TYPE           Type of backup to execute: rsync / tar
  -D --dryrun                   Run the code without executing the backup command.
  -d --debug                    Enable debug logging.
  -s --stdin                    Get configuration from STDIN as well.
  -b --battery-check            Enable checking for battery power before running.
  -f --force                    When used things like running on battery are ignored.

""".format(
    version=__version__,
    config=','.join(config.DEFAULT_CONFIG_FILE_ORDER)
)

def main(argv=sys.argv):
    opts = docopt(HELP, argv=argv, version='rbackup 0.1')

    LOG = setup_logging(log_file=opts['--log'], debug=opts['--debug'])

    conf = utils.read_config(opts['--config'].split(','), opts['--stdin'])
    if not conf:
        LOG.error('No config file found!')
        sys.exit(1)

    assets, targets = utils.parse_config(conf)

    if opts['config']:
        utils.print_config(assets, targets)
        sys.exit(0)

    if opts['--pid']:
        if not utils.process_is_alone(opts['--pid'], force=opts['--force']):
            LOG.warning('Aborting due to use of --one-instance')
            sys.exit(1)

    if opts['--battery-check'] and not opts['--force']:
        if utils.on_battery():
            LOG.warning('System running on battery. Aborting.')
            sys.exit(0)

    if opts['restore']:
        LOG.warning('Enabled RESTORE mode!')

    for asset_id in opts['<asset>']:
        asset = assets.get(asset_id)

        if asset is None:
            LOG.error('No such asset exists in config: %s', asset_id)
            continue

        target = targets.get(asset.target)
        if target is None:
            LOG.error('Invalid target for asset %s: %s', asset.id, asset.target)
            continue
        if not target.available() and not opts['--force']:
            LOG.error('Skipping asset: %s', asset.id)
            continue

        # overrride type with options
        if opts['--type']:
            asset.type = opts['--type']
        if opts['--timeout']:
            asset.type = opts['--timeout']

        sync(asset, target, opts['restore'], opts['--dryrun'])

if __name__ == "__main__": # pragma: no cover
    main()
