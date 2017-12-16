from pytest import mark
from pytest import raises
from mock import patch, Mock
from sh import ErrorReturnCode

from rbackup.execute import signal_handler, execute
from rbackup.execute import TimeoutException as TOutExc

class SHError(ErrorReturnCode):
    def __init__(self):
        super(SHError, self).__init__('cmd', b'stdout', b'stderr')

class KBInter(KeyboardInterrupt):
    pass

def test_signal_handler():
    with raises(TOutExc):
        signal_handler(None, None)

@mark.parametrize(
    ['command', 'proc',                      'piped', 'timeout'], [
    (Mock(),    Mock(),                      None,     None),
    (Mock(),    Mock(),                      Mock(),   None),
    (Mock(),    Mock(),                      Mock(),   1000),
    (Mock(),    Mock(side_effect=KBInter()), None,     None),
    (Mock(),    Mock(side_effect=KBInter()), Mock(),   None),
    (Mock(),    Mock(side_effect=KBInter()), Mock(),   1000),
    (Mock(),    Mock(side_effect=TOutExc()), None,     None),
    (Mock(),    Mock(side_effect=TOutExc()), None,     1000),
    (Mock(),    Mock(side_effect=TOutExc()), Mock(),   1000),
    (Mock(),    Mock(side_effect=SHError()), None,     None),
    (Mock(),    Mock(side_effect=SHError()), Mock(),   None),
    (Mock(),    Mock(side_effect=SHError()), Mock(),   1000),
])
@patch('rbackup.execute.sh')
@patch('rbackup.execute.signal')
def test_execute(m_signal, m_sh, command, proc, piped, timeout):
    command.return_value = proc
    rval = execute(command, piped, timeout)
    assert rval == proc

