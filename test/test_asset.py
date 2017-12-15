from unittest import TestCase
from rbackup.asset import Asset

class TestAsset(TestCase):

    def test_constructor(self):
        a = Asset('some_id', 'some_src', target='some_target')
        assert a.id == 'some_id'
        assert a.src == 'some_src'
        assert a.target == 'some_target'
        assert a.dest == ''
        assert a.opts == []
        assert a.exclude == []

    def test_from_dict(self):
        a = Asset.from_dict({
            'id': 'some_id',
            'src': 'some_src',
            'target': 'some_target',
        })
        assert a.id == 'some_id'
        assert a.src == 'some_src'
        assert a.target == 'some_target'
        assert a.dest == ''
        assert a.opts == []
        assert a.exclude == []
