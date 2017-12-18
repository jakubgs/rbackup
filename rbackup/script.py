import sys
import argparse

from rbackup import utils, config
from rbackup.log import setup_logging
from rbackup.sync import sync

try:
    import sh
except ImportError:
    print('Failed to import module "sh". Please install it.')
    sys.exit(1)


HELP_MESSAGE = """
This script backups directories configred as 'assets' in the YAML config file.

Configuration can be also provided through standard input using --stdin flag..
The config is merged with the one read from the file.

Config file locations read in the following order:
* {}
""".format('\n* '.join(config.DEFAULT_CONFIG_FILE_ORDER))


def create_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=HELP_MESSAGE)

    parser.add_argument( "-a", "--assets", nargs='+', type=str,
                        default=config.DEFAULT_PID_FILE,
                        help="List of assets to process.")
    parser.add_argument("-t", "--type", type=str,
                        help="Type of backup to execute: rsync / tar")
    parser.add_argument("-T", "--timeout", type=int, default=config.DEFAULT_TIMEOUT,
                        help="Time after which rsync command will be stopped.")
    parser.add_argument("-p", "--pid-file", type=str, default=config.DEFAULT_PID_FILE,
                        help="Location of the PID file.")
    parser.add_argument("-l", "--log-file", type=str, default=config.DEFAULT_LOG_FILE,
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
    parser.add_argument("-P", "--print-config", action='store_true',
                        help="Show current configuration of sources and targets.")
    parser.add_argument("-b", "--battery-check", action='store_true',
                        help="Enable checking for battery power before running.")
    parser.add_argument("-f", "--force", action='store_true',
                        help="When used things like running on battery are ignored.")
    parser.add_argument("-c", "--config", type=str,
                        default=','.join(config.DEFAULT_CONFIG_FILE_ORDER),
                        help="Location of YAML config file.")
    return parser.parse_args()


def main():
    opts = create_arguments()
    LOG = setup_logging(opts.log_file, debug=opts.debug)

    conf = utils.read_config(opts.config.split(','), opts.stdin)
    if not conf:
        LOG.error('No config file found!')
        sys.exit(1)

    assets, targets = utils.parse_config(conf)

    if opts.print_config:
        utils.print_config(assets, targets)
        sys.exit(0)

    if opts.one_instance and not utils.process_is_alone(opts.pid_file, force=opts.force):
        LOG.warning('Aborting due to use of --one-instance')
        sys.exit(1)

    if opts.battery_check and not opts.force and utils.on_battery():
        LOG.warning('System running on battery. Aborting.')
        sys.exit(0)

    if opts.restore:
        LOG.warning('Enabled RESTORE mode!')

    for asset_id in opts.assets:
        asset = assets.get(asset_id)

        if asset is None:
            LOG.error('No such asset exists in config: %s', asset_id)
            continue

        target = targets.get(asset.target)
        if target is None:
            LOG.error('Invalid target for asset %s: %s', asset.id, asset.target)
            continue
        if not target.available() and not opts.force:
            LOG.error('Skipping asset: %s', asset.id)
            continue

        # overrride type with options
        if opts.type:
            asset.type = opts.type

        sync(asset, target, opts.timeout, opts.restore, opts.dryrun)

if __name__ == "__main__":
    main()
