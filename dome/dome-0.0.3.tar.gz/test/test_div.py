from unittest import TestCase
from dome import dome as D


class TestDiv(TestCase):
    def test_single(self):
        self.assertEquals('<div/>', D.Div().dumps())
        self.assertEquals('<div>hehe</div>', D.Div('hehe').dumps())

    def test_all(self):
        node = D.Html(
            D.Head(
                D.Meta(Charset="utf-8"),
                D.Meta(HttpEquiv='X-UA-Compatible', Content='IE=edge,chrome=1'),
                D.Node('title')('This is Title')
            ),
            D.Body(
                D.Div(
                    'div #1',
                    Id='1st', Class='cs1',
                ), "\n",
                D.Div(
                    'div #2',
                    Id='2nd', Style="display: none",
                )
            )
        )
        self.assertEquals('<html><head><meta charset="utf-8"/><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/><title>This is Title</title></head><body><div id="1st" class="cs1">div #1</div>\n<div id="2nd" style="display: none">div #2</div></body></html>',
                          node.dumps())
    
    def test_partial(self):
        pass