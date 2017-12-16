from pytest import raises, mark
from mock import patch, mock_open
from unittest import TestCase
import rbackup.utils as util

@mark.parametrize( ['data', 'expected'], [
    ('Unknown', False),
    ('Discharging', True),
])
@patch('rbackup.utils.glob.glob')
def test_on_battery(m_glob, data, expected):
    m_glob.return_value = ['bat1', 'bat2']
    with patch("builtins.open", mock_open(read_data=data)) as m_file:
        rval = util.on_battery() 
        assert rval is expected

@mark.parametrize(['kill_result', 'expected'], [
    (None, True),
    (Exception('TEST'), False),
])
@patch('rbackup.utils.os.kill')
def test_proc_exists(m_kill, kill_result, expected):
    m_kill.side_effect = kill_result
    rval = util.proc_exists(666)
    assert rval is expected

@mark.parametrize(['file_is', 'pid'], [
    (True,  1234),
    (True,  None),
    (False, None),
])
@patch('rbackup.utils.proc_exists')
@patch('rbackup.utils.os.path.isfile')
def test_check_process_(m_isfile, m_proc_exists, file_is, pid):
    m_isfile.return_value = file_is
    m_proc_exists.return_value = pid
    with patch("builtins.open", mock_open(read_data='1234')) as m_file:
        rval = util.check_process('pid_file')
        assert rval == (file_is, pid)
        assert m_proc_exists.calledWith(1234)

@patch('rbackup.utils.os.remove')
def test_exit_handler(m_remove):
    util.exit_handler()
    assert m_remove.called
 
@mark.parametrize(
    ['file_is', 'pid', 'force', 'expected'], [
    (True,      1234,  False,   False),
    (True,      None,  False,   False),
    (True,      None,  True,    True),
    (False,     None,  False,   True),
])
@patch('rbackup.utils.LOG')
@patch('rbackup.utils.exit_handler')
@patch('rbackup.utils.check_process')
@patch('rbackup.utils.atexit.register')
def test_process_is_alone_exit(m_register, m_check_process, m_exit_handler, m_log,
                               file_is, pid, force, expected):
    m_check_process.return_value = (file_is, pid)
    rval = util.process_is_alone('pid_file', force)
    assert rval is expected
    assert m_register.called
