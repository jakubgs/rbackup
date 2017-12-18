import sys
from pytest import raises, mark
from mock import Mock, patch, mock_open

import rbackup.utils as util
from rbackup.asset import Asset
from rbackup.target import Target


# horrible but necessary to mock open
open_name = 'builtins.open'
if sys.version_info[0] < 3:
    open_name = '__builtin__.open'

@mark.parametrize( ['data', 'expected'], [
    ('Unknown', False),
    ('Discharging', True),
])
@patch('rbackup.utils.glob.glob')
def test_on_battery(m_glob, data, expected):
    m_glob.return_value = ['bat1', 'bat2']
    print('WTF:', open_name)
    with patch(open_name, mock_open(read_data=data)) as m_file:
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
    with patch(open_name, mock_open(read_data='1234')) as m_file:
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
@patch('rbackup.utils.exit_handler')
@patch('rbackup.utils.check_process')
@patch('rbackup.utils.atexit.register')
def test_process_is_alone_exit(m_register, m_check_process, m_exit_handler,
                               file_is, pid, force, expected):
    m_check_process.return_value = (file_is, pid)
    rval = util.process_is_alone('pid_file', force)
    assert rval is expected
    assert m_register.called

@mark.parametrize(
    ['open_mock',                  'expected'], [
    (mock_open(read_data='data'),  'data'),
    (Mock(side_effect=IOError()),  None),
])
def test_read_config_file(open_mock, expected):
    with patch(open_name, open_mock) as m_file:
        rval = util.read_config_file(['file_a'])
    assert rval == expected

@mark.parametrize(
    ['cfile',          'stdin'], [
    ({'test': 'TEST'}, {}),
    ({'test': 'TEST'}, {'TEST': 'test'}),
])
@patch('rbackup.utils.read_config_stdin')
@patch('rbackup.utils.read_config_file')
def test_read_config(m_read_file, m_read_stdin, cfile, stdin):
    m_read_file.return_value = cfile
    m_read_stdin.return_value = stdin
    expected = cfile.copy()
    expected.update(stdin)
    rval = util.read_config(config_files=['file_a'], stdin=bool(stdin))
    assert rval == expected

def test_parse_config():
    config = {
        'assets': [ { 'id': 'asset_1', 'src': '/some/path' } ],
        'targets': [ { 'id': 'target_1', 'dest': '/another/path' } ],
    }
    assets, targets = util.parse_config(config)
    assert isinstance(assets['asset_1'], Asset)
    assert isinstance(targets['target_1'], Target)

@mark.parametrize(
    ['select_return',      'expected'], [
    ((True, None, None),   True),
    ((False, None, None),  False),
])
@patch('rbackup.utils.select.select')
def test_file_has_input(m_select, select_return, expected):
    m_select.return_value = select_return
    rval = util.file_has_input('some_file')
    assert rval == expected

@mark.parametrize(
    ['isatty',  'has_input', 'loaded',      'expected'], [
    (True,     None,         None,          {}),
    (False,    False,        None,          {}),
    (False,    True,         {'t': 'T'},    {'t': 'T'}),
    (False,    True,         ValueError(),  {}),
])
@patch('rbackup.utils.file_has_input')
@patch('rbackup.utils.sys.stdin.isatty')
@patch('rbackup.utils.yaml.load')
def test_read_config_stdin(m_load, m_isatty, m_has_input, isatty, has_input, loaded, expected):
    m_load.side_effect = [loaded]
    m_isatty.return_value = isatty
    m_has_input.return_value = has_input
    rval = util.read_config_stdin()
    assert rval == expected

def test_print_config():
    assets = {
        'asset_1': Asset('asset_1', '/some/path'),
        'asset_2': Asset('asset_1', '/moar/paths', target='target_1'),
    }
    targets = {
        'target_1': Target('target_1', '/another/path'),
    }
    util.print_config(assets, targets)
