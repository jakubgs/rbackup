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

def PMock(wait=None):
    m = Mock()
    if wait:
        m.wait = Mock(side_effect=wait)
    return m

@mark.parametrize(
    ['command', 'proc',                'piped', 'timeout', 'expected'], [
    (Mock(),    PMock(),               None,    None,      True),
    (Mock(),    PMock(),               Mock(),  None,      True),
    (Mock(),    PMock(wait=KBInter()), None,    None,      None),
    (Mock(),    PMock(wait=KBInter()), Mock(),  None,      None),
    (Mock(),    PMock(wait=TOutExc()), None,    1000,      None),
    (Mock(),    PMock(wait=TOutExc()), None,    1000,      None),
    (Mock(),    PMock(wait=TOutExc()), Mock(),  1000,      None),
    (Mock(),    PMock(wait=SHError()), None,    None,      None),
    (Mock(),    PMock(wait=SHError()), Mock(),  None,      None),
])
@patch('rbackup.execute.signal')
def test_execute(m_signal, command, proc, piped, timeout, expected):
    command.return_value = proc
    rval = execute(command, piped, timeout)
    if expected is None:
        assert rval is None
    else:
        assert rval == proc
    print('WAT:', type(proc.side_effect))
    print('WTF:', isinstance(proc.side_effect, SHError))
    if proc.side_effect and not isinstance(proc.side_effect, SHError):
        assert proc.terminate.called
        assert proc.kill.called

