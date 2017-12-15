import logging

LOG = logging.getLogger('backup')

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


