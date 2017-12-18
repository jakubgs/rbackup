from mock import patch
from logging import Logger, INFO, DEBUG
from rbackup.log import setup_logging


@patch('rbackup.log.logging.FileHandler')
def test_setup_logging(m_fhandler):
    log = setup_logging('test_file')
    assert isinstance(log, Logger)
    assert log.level == INFO
    assert m_fhandler.called
    log.removeHandler(log.handlers[0])

@patch('rbackup.log.logging.FileHandler')
def test_setup_logging_debug(m_fhandler):
    log = setup_logging('test_file', debug=True)
    assert isinstance(log, Logger)
    assert log.level == DEBUG
    assert m_fhandler.called
    log.removeHandler(log.handlers[0])
