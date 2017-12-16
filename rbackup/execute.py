import sh
import time
import signal
from log import LOG

class TimeoutException(Exception):
    pass


def signal_handler(signum, frame):
    raise TimeoutException('Timed out!')


def execute(command, piped=None, timeout=None):
    LOG.debug('CMD: %s', command)
    if piped:
        LOG.debug('PIPED: %s', piped)

    if timeout:
        # prepare timer to kill command if it runs too long
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(timeout)
        LOG.debug('Command timeout: %s', timeout)

    try:
        start = time.time()

        if piped:
            proc = command(piped(), _bg=True)
        else:
            proc = command(_bg=True)
            
        proc.wait()

        end = time.time()
    except KeyboardInterrupt as e:
        LOG.warning('Command stopped by KeyboardInterrupt!')
        proc.terminate()
        proc.kill()
        LOG.warning('Killed process: {}'.format(proc.pid))
        return None
    except TimeoutException as e:
        proc.terminate()
        proc.kill()
        LOG.error('Command timed out after {} seconds!'.format(timeout))
        return None
    except sh.ErrorReturnCode as e:
        LOG.error('Failed to execute command: %s', command)
        LOG.error('Output:\n{}'.format(
            e.stderr or getattr(proc, 'stderr')))
        return None
    LOG.info('Finished in: {}s'.format(round(end - start, 2)))
    return proc


