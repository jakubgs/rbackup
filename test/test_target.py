from pytest import mark
from pytest import raises
from mock import patch, Mock

from rbackup.target import Target


@patch('rbackup.target.getuser')
def test_target_constructor(m_getuser):
    m_getuser.return_value = 'mock_user'
    t = Target('target_id', '/some/path')
    assert t.id == 'target_id'
    assert t.dest == '/some/path'
    assert t.user == 'mock_user'
    assert t.host == 'localhost'
    assert t.port == 22
    assert t.ping == False

def test_target_constructor():
    data = {
        'id': 'target_id',
        'dest': '/some/path',
        'user': 'test_user',
        'host': 'bkp.example.net',
        'port': 666,
        'ping': True,
    }
    t = Target.from_dict(data)
    assert t.id == 'target_id'
    assert t.dest == '/some/path'
    assert t.user == 'test_user'
    assert t.host == 'bkp.example.net'
    assert t.port == 666
    assert t.ping == True
 
@mark.parametrize(
    ['ssh', 'ping'], [
    (True,  True),
    (False, True),
    (True,  False),
    (False, False),
])
@patch('rbackup.target.Target._ping_check')
@patch('rbackup.target.Target._ssh_check')
def test_available(m_ssh_check, m_ping_check, ssh, ping):
    m_ssh_check.return_value = ssh
    m_ping_check.return_value = ping
    t = Target('target_id', '/some/path')
    rval = t.available()
    assert rval == (ssh and ping)

@patch('rbackup.target.sh')
def test__ssh_check_ok(m_sh):
    t = Target('target_id', '/some/path')
    rval = t._ssh_check(timeout=1)
    assert rval == True

@patch('rbackup.target.sh')
def test__ssh_check_fail(m_sh):
    m_sh.ssh.bake.return_value = m_sh
    m_sh.bake.return_value = m_sh
    m_sh.exit.side_effect = Exception('TEST')
    t = Target('target_id', '/some/path')
    rval = t._ssh_check(timeout=1)
    assert rval == False

@mark.parametrize(
    ['ping', 'host',    'sh',                                'expected'], [
    (True,   'example', Mock(stdout='ttl=64 time=0.123 ms'), True),
    (True,   'example', Mock(stdout='ttl=64 time=1.123 ms'), False),
    (True,   'example', Exception('TEST'),                   False),
    (False,  'example', None,                                True),
])
@patch('rbackup.target.sh')
def test__ping_check_ok(m_sh, ping, host, sh, expected):
    '64 bytes from localhost icmp_seq=1 '
    m_sh.ping.bake.return_value = m_sh
    m_sh.side_effect = [sh]
    t = Target('target_id', '/some/path', host=host, ping=ping)
    rval = t._ping_check(min_ping=1)
    assert rval == expected
