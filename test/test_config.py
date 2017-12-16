from mock import patch
from unittest import TestCase
import rbackup.config as config

class TestConfig(TestCase):

    def test_defaults_exist(self):
        assert isinstance(config.DEFAULT_CONFIG_FILE_ORDER, list)
        assert isinstance(config.DEFAULT_PID_FILE, str)
        assert isinstance(config.DEFAULT_LOG_FILE, str)
        assert isinstance(config.DEFAULT_MINIMAL_PING, int)
        assert isinstance(config.DEFAULT_TIMEOUT, int)
