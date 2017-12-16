from mock import patch
from logging import Logger, INFO, DEBUG
from unittest import TestCase
from rbackup.log import setup_logging

class TestLog(TestCase):

    @patch('rbackup.log.logging.FileHandler')
    def test_setup_logging(self, m_fhandler):
        log = setup_logging('test_file')
        assert isinstance(log, Logger)
        assert log.level == INFO
        assert m_fhandler.called

    @patch('rbackup.log.logging.FileHandler')
    def test_setup_logging_debug(self, m_fhandler):
        log = setup_logging('test_file', debug=True)
        assert isinstance(log, Logger)
        assert log.level == DEBUG
        assert m_fhandler.called
