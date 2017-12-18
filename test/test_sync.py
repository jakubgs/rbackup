import logging
from pytest import mark, fixture, raises
from mock import patch, Mock

from rbackup.asset import Asset
from rbackup.target import Target
from rbackup import sync

@fixture
def rsync_output():
    return [
        'Number of files: 53,051 (reg: 45,676, dir: 7,246, link: 129)',
        'Number of created files: 0',
        'Number of deleted files: 0',
        'Number of regular files transferred: 13',
        'Total file size: 360.77M bytes',
        'Total transferred file size: 421.69K bytes',
        'Literal data: 421.69K bytes',
        'Matched data: 0 bytes',
        'File list size: 1.18M',
        'File list generation time: 1.024 seconds',
        'File list transfer time: 0.000 seconds',
        'Total bytes sent: 1.67M',
        'Total bytes received: 283',
        'sent 1.67M bytes  received 283 bytes  1.11M bytes/sec',
        'total size is 360.77M  speedup is 216.61',
    ]

@fixture
def asset():
    return Asset(
        'asset_id',
        '/asset/path',
        target='target_id',
        timeout=666,
        dest='bkp'
    )

@fixture
def target():
    return Target('target_id', '/target/path', host='bkp.example.net', user='testuser')

@patch('rbackup.sync.LOG')
def test__log_rsync_stats(m_log, rsync_output):
    sync._log_rsync_stats('\n'.join(rsync_output))
    print(m_log.info.call_args_list[0][0][0])
    for call in m_log.info.call_args_list:
        assert 'sent' in call[0][0] or 'total size' in call[0][0]
    for call in m_log.debug.call_args_list:
        assert call[0][0] in rsync_output

def test__make_full_dest(asset, target):
    rval = sync._make_full_dest(asset, target)
    assert rval == 'testuser@bkp.example.net:/target/path/bkp'

def test__make_full_dest_local(asset, target):
    target.id = 'local'
    target.dest = '/'
    rval = sync._make_full_dest(asset, target)
    assert rval == '/bkp'

def test__bake_rsync_for_target(asset, target):
    asset.opts = {'test': 'TEST'}
    asset.exclude = ['something']
    rval = sync._bake_rsync_for_target(asset, target)
    assert set(str(rval).split()) == set([
        '/usr/bin/rsync', '--archive', '--recursive', '--update', '--times',
        '--partial', '--stats', '--human-readable', '--delete-after',
        '--delete-excluded', '--rsh=ssh', '-p', '22',
        '--test=TEST', '--timeout=666', '--exclude=something',
    ])

@mark.parametrize('type', ['rsync', 'tar'])
@patch('rbackup.sync.r_sync')
@patch('rbackup.sync.tar_ssh')
def test_sync_ok(m_tar_ssh, m_r_sync, type, asset, target):
    mocks = {
        'tar': m_tar_ssh,
        'rsync': m_r_sync,
    }
    asset.type = type
    rval = sync.sync(asset, target, 1000)
    assert rval == mocks[type].return_value

def test_sync_fail(asset, target):
    asset.type = 'unknown'
    with raises(Exception):
        sync.sync(asset, target, 1000)

@mark.parametrize(
    ['restore', 'dryrun'], [
    (False,     False),
    (True,      False),
    (False,     True),
    (True,      True),
])
@patch('rbackup.sync.execute')
@patch('rbackup.sync._log_rsync_stats')
@patch('rbackup.sync._bake_rsync_for_target')
def test_r_sync(m_rsync_bake, m_log_stats, m_execute, asset, target, restore, dryrun):
    rval = sync.r_sync(asset, target, restore=restore, dryrun=dryrun)
    if dryrun:
        assert rval == None
    else:
        assert rval == m_execute.return_value

@mark.parametrize('dryrun', [False, True])
@patch('rbackup.sync.execute')
@patch('rbackup.sync._log_rsync_stats')
@patch('rbackup.sync._bake_rsync_for_target')
def test_tar_ssh(m_rsync_bake, m_log_stats, m_execute, asset, target, dryrun):
    asset.exclude = ['something']
    rval = sync.tar_ssh(asset, target, dryrun=dryrun)
    if dryrun:
        assert rval == None
    else:
        assert rval == m_execute.return_value
