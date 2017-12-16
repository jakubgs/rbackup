from pytest import mark
from mock import patch, mock_open
from unittest import TestCase
import rbackup.utils as util

@mark.parametrize( ['data', 'expect'], [
    ('Unknown', False),
    ('Discharging', True),
])
@patch('rbackup.utils.glob.glob')
def test_on_battery(m_glob, data, expect):
    m_glob.return_value = ['bat1', 'bat2']
    with patch("builtins.open", mock_open(read_data=data)) as m_file:
        rval = util.on_battery() 
        assert rval is expect

@mark.parametrize(['kill_result', 'expect'], [
    (None, True),
    (Exception('TEST'), False),
])
@patch('rbackup.utils.os.kill')
def test_proc_exists(m_kill, kill_result, expect):
    m_kill.side_effect = kill_result
    rval = util.proc_exists(666)
    assert rval is expect

@mark.parametrize(['file_is', 'process_is'], [
    (True, True),
    (True, False),
    (False, False),
])
@patch('rbackup.utils.proc_exists')
@patch('rbackup.utils.os.path.isfile')
def test_check_process_(m_isfile, m_proc_exists, file_is, process_is):
    m_isfile.return_value = file_is
    m_proc_exists.return_value = process_is
    with patch("builtins.open", mock_open(read_data='pid')) as m_file:
        rval = util.check_process('pid_file')
        assert rval == (file_is, process_is)
        assert m_proc_exists.calledWith('pid')


@patch('rbackup.utils.os.remove')
def test_exit_handler(m_remove):
    util.exit_handler()
    assert m_remove.called
