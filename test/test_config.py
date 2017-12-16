from mock import patch
import rbackup.config as config

def test_defaults_exist():
    assert isinstance(config.DEFAULT_CONFIG_FILE_ORDER, list)
    assert isinstance(config.DEFAULT_PID_FILE, str)
    assert isinstance(config.DEFAULT_LOG_FILE, str)
    assert isinstance(config.DEFAULT_MINIMAL_PING, int)
    assert isinstance(config.DEFAULT_TIMEOUT, int)
