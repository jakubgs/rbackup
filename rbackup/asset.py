class Asset(object):

    def __init__(self, id, src, target='local',
                 type=None, timeout=None,
                 dest='', opts=[], exclude=[]):
        self.id = id
        self.target = target
        self.src = src
        self.type = type or 'rsync'
        self.dest = dest or ''
        self.opts = opts
        self.timeout = timeout
        self.exclude = exclude

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['id'],
            data['src'],
            target=data.get('target', 'local'),
            type=data.get('type', 'rsync'),
            dest=data.get('dest', ''),
            opts=data.get('opts', []),
            timeout=data.get('timeout', None),
            exclude=data.get('exclude', []),
        )
