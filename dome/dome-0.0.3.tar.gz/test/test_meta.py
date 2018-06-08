from unittest import TestCase
from dome import dome as D


class TestMeta(TestCase):
    def test_single(self):
        self.assertEquals('<meta/>', D.Meta().dumps())

    def test_all(self):
        pass
    
    def test_partial(self):
        pass