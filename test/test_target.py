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
@patch('rbackup.target.ping_works')
@patch('rbackup.target.ssh_works')
def test_available(m_ssh_works, m_ping_works, ssh, ping):
    m_ssh_works.return_value = ssh
    m_ping_works.return_value = ping
    t = Target('target_id', '/some/path')
    rval = t.available()
    assert rval == (ssh and ping)
