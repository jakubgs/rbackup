from pytest import mark
from mock import patch, Mock

from rbackup.target import Target
from rbackup.check import ssh_works, ping_works

@patch('rbackup.check.sh')
def test_ssh_works_ok(m_sh):
    t = Target('target_id', '/some/path')
    rval = ssh_works(t, timeout=1)
    assert rval == True

@patch('rbackup.check.sh')
def test_ssh_works_local(m_sh):
    t = Target('local', '/some/path')
    rval = ssh_works(t, timeout=1)
    assert rval == True

@patch('rbackup.check.sh')
def test_ssh_works_fail(m_sh):
    m_sh.ssh.bake.return_value = m_sh
    m_sh.bake.return_value = m_sh
    m_sh.exit.side_effect = Exception('TEST')
    t = Target('target_id', '/some/path')
    rval = ssh_works(t, timeout=1)
    assert rval == False

@mark.parametrize(
    ['ping', 'host',    'sh',                                'expected'], [
    (True,   'example', Mock(stdout='ttl=64 time=0.123 ms'), True),
    (True,   'example', Mock(stdout='ttl=64 time=1.123 ms'), False),
    (True,   'example', Exception('TEST'),                   False),
    (False,  'example', None,                                True),
])
@patch('rbackup.check.sh')
def test_ping_works_ok(m_sh, ping, host, sh, expected):
    '64 bytes from localhost icmp_seq=1 '
    m_sh.ping.bake.return_value = m_sh
    m_sh.side_effect = [sh]
    t = Target('target_id', '/some/path', host=host, ping=ping)
    rval = ping_works(t, min_ping=1)
    assert rval == expected
