from getpass import getuser

from rbackup.check import ssh_works, ping_works


class Target(object):

    def __init__(self, id, dest, user=None, host='localhost', port=22, ping=False):
        assert id is not None
        assert dest is not None
        self.id = id
        self.dest = dest
        self.user = user or getuser()
        self.host = host
        self.port = port
        self.ping = ping

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('id'),
                data.get('dest'),
                user=data.get('user', getuser()),
                host=data.get('host', 'localhost'),
                port=data.get('port', 22),
                ping=data.get('ping', False),
        )

    def available(self):
        return ping_works(self) and ssh_works(self)
