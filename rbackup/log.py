import sys
import logging

LOG = logging.getLogger('backup')

STDOUT_FORMAT = '%(levelname)s: %(message)s'
FILE_FORMAT = '%(asctime)s - {}'.format(STDOUT_FORMAT)

def setup_logging(log_file, debug):
    logging.basicConfig(format=STDOUT_FORMAT)

    log = logging.getLogger('backup')
    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    fhandler = logging.FileHandler(log_file)
    fhandler.setFormatter(logging.Formatter(FILE_FORMAT))
    log.addHandler(fhandler)
    return log


