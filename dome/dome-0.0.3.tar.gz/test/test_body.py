from unittest import TestCase
from dome import dome as D


class TestBody(TestCase):
    def test_single(self):
        self.assertEquals('<body/>', D.Body().dumps())
        self.assertEquals('<body>hehe</body>', D.Body('hehe').dumps())

    def test_all(self):
        pass
    
    def test_partial(self):
        pass