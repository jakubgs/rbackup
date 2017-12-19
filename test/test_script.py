from pytest import raises, mark
from mock import Mock, patch, mock_open

from rbackup.script import main


@mark.parametrize(
    ['called','avail','target_id', 'argv'], [
    (True,    True,   'target_id', ['save', 'asset_id']),
    (False,    False,  'target_id', ['save', 'asset_id']),
    (False,   True,   'no_target', ['save', 'asset_id']),
    (False,   True,   'target_id', ['save', 'no_such_asset_id']),
    (True,    True,   'target_id', ['save', 'asset_id', '--type', 'tar']),
    (True,    True,   'target_id', ['save', 'asset_id', '--timeout', '1000']),
    (True,    True,   'target_id', ['save', 'asset_id', '--debug']),
    (True,    True,   'target_id', ['save', 'asset_id', '--pid', '/pid/file']),
    (True,    True,   'target_id', ['save', 'asset_id', '--battery-check']),
    (True,    True,   'target_id', ['restore', 'asset_id']),
    (False,   False,  'target_id', ['restore', 'asset_id']),
    (False,   True,   'no_target', ['restore', 'asset_id']),
])
@patch('rbackup.script.utils')
@patch('rbackup.script.sync')
def test_main_ok(m_sync, m_utils, asset, target, called, avail, target_id, argv):
    asset.target = target_id
    target.available.return_value = avail
    m_utils.on_battery.return_value = False
    m_utils.parse_config.return_value = (
        {'asset_id': asset}, {'target_id': target}
    )
    main(argv=argv)
    assert m_sync.called == called

@patch('rbackup.script.utils')
def test_main_on_battery(m_utils, asset, target):
    m_utils.on_battery.return_value = True
    m_utils.parse_config.return_value = ('x', 'y')
    with raises(SystemExit):
        main(argv=['save', 'asset_id', '--battery-check'])

@patch('rbackup.script.utils')
def test_main_another_process(m_utils, asset, target):
    m_utils.process_is_alone.return_value = False
    m_utils.parse_config.return_value = ('x', 'y')
    with raises(SystemExit):
        main(argv=['save', 'asset_id', '--pid', '/pid/file'])

@patch('rbackup.script.utils')
def test_main_no_config(m_utils, asset, target):
    m_utils.read_config.return_value = None
    argv = ['save', 'asset_id', '--debug']
    with raises(SystemExit):
        main(argv)
    assert not m_utils.parse_config.called

@patch('rbackup.script.utils')
def test_main_print_config(m_utils, asset, target):
    m_utils.parse_config.return_value = ('x', 'y')
    with raises(SystemExit):
        main(argv=['config'])
    assert m_utils.print_config.called
