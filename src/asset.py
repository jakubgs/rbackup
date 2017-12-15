class Asset(object):

    def __init__(self, id, target, src, type=None, dest='', opts=[], exclude=[]):
        self.id = id
        self.target = target
        self.src = src
        self.type = type or 'rsync'
        self.dest = dest or ''
        self.opts = opts
        self.exclude = exclude

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('id'),
                data.get('target'),
                data.get('src'),
                type=data.get('type'),
                dest=data.get('dest'),
                opts=data.get('opts'),
                exclude=data.get('exclude'),
        )
