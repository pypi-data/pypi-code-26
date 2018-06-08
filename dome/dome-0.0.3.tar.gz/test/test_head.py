from unittest import TestCase
from dome import dome as D


class TestHeader(TestCase):
    def test_single(self):
        self.assertEquals('<head/>', D.Head().dumps())
        self.assertEquals('<head>hehe</head>', D.Head('hehe').dumps())

    def test_all(self):
        pass
    
    def test_partial(self):
        pass