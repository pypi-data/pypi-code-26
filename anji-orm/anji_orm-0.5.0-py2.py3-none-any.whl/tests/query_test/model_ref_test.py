from anji_orm import Model, StringField

from ..base import BaseTestCase


class T1(Model):

    _table = 'non_table'

    c1 = StringField()
    c2 = StringField()


class QueryMergeTest(BaseTestCase):

    def test_query_row(self):
        self.assertEqual(T1.c1.model_ref, T1)

    def test_query_qe(self):
        self.assertEqual((T1.c1 >= 5).model_ref, T1)

    def test_query_qt(self):
        self.assertEqual((T1.c1 > 5).model_ref, T1)

    def test_query_le(self):
        self.assertEqual((T1.c1 <= 5).model_ref, T1)

    def test_query_lt(self):
        self.assertEqual((T1.c1 < 5).model_ref, T1)

    def test_query_eq(self):
        self.assertEqual((T1.c1 == 5).model_ref, T1)

    def test_query_neq(self):
        self.assertEqual((T1.c1 != 5).model_ref, T1)

    def test_query_bound(self):
        self.assertEqual(((T1.c1 >= 5) & (T1.c1 < 6)).model_ref, T1)

    def test_query_bound_with_bound(self):
        self.assertEqual(
            (
                ((T1.c1 >= 5) & (T1.c1 < 6)) & ((T1.c1 >= 5.3) & (T1.c1 < 5.5))
            ).model_ref,
            T1
        )
