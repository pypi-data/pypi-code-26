from unittest import TestCase
from dome import dome as D


class TestHtml(TestCase):
    def test_single(self):
        self.assertEquals('<html/>', D.Html().dumps())
        self.assertEquals('<html>hehe</html>', D.Html('hehe').dumps())

    def test_all(self):
        pass

    def test_partial(self):
        pass