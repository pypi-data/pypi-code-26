# pylint: disable=invalid-name
import asyncio
import unittest
from datetime import timedelta

import asynctest

from anji_orm import orm_register

from .models import T1


class SyncTestSkeleton(unittest.TestCase):

    @classmethod
    def generate_connection_uri(cls):
        return None, {}

    @classmethod
    def setUpClass(cls):
        connection_uri, pool_kwargs = cls.generate_connection_uri()
        if connection_uri is None:
            raise unittest.SkipTest("Skip abstrac class")
        orm_register.init(connection_uri, pool_kwargs)

    def setUp(self):
        orm_register.load()

    def tearDown(self):
        orm_register.sync_strategy.drop_table(T1._table)

    @classmethod
    def tearDownClass(cls):
        orm_register.close()

    def test_base_interaction(self):
        t1 = T1(c1='5', c2='6')
        t2 = T1(c1='6', c2='7')
        t1.send()
        t2.send()
        t1_list = T1.all().run()
        self.assertEqual(len(t1_list), 2)

    def test_simple_search(self):
        for c1 in map(str, range(0, 10)):
            T1(c1=c1, c2='5').send()
        t1_list = (T1.c1 > '5').run()
        self.assertEqual(len(t1_list), 4)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    def test_magic_update(self):
        t1_1 = T1(c1='5', c2='6')
        t1_1.send()
        t1_2 = T1.all().run()[0]
        t1_2.c2 = '7'
        t1_2.send()
        t1_1.load()
        self.assertEqual(t1_1.c2, '7')

    def test_datetime(self):
        test_datetime = orm_register.current_utc_datetime() + timedelta(minutes=5)
        t1_original = T1(c3=test_datetime)
        t1_original.send()
        t1_1 = T1.all().run()[0]
        self.assertEqual(t1_1.c3, t1_original.c3)
        t1_2 = (T1.c3 == test_datetime).run()[0]
        self.assertEqual(t1_2.c3, t1_original.c3)

    def test_complex_search(self):
        for c1 in map(str, range(0, 10)):
            T1(c1=c1, c2='5').send()
        t1_list = ((T1.c1 > '5') & (T1.c1 < '8')).run()
        self.assertEqual(len(t1_list), 2)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    def test_sotring(self):
        for c1 in map(str, range(0, 3)):
            for c2 in map(str, range(0, 3)):
                T1(c1=c1, c2=c2).send()
        t1_list = T1.all().order_by(T1.c1.amount.desc(), T1.c2.amount.desc()).run()
        self.assertEqual(t1_list[0].c1, '2')
        self.assertEqual(t1_list[0].c2, '2')

    def test_nested_queries(self):
        t1 = T1(c4={"c2": 5})
        t1.send()
        t1_search = (T1.c4.c2 == 5).run()[0]
        self.assertEqual(t1.c4, t1_search.c4)

    def test_complex_nested_queries(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        t1_list = ((T1.c4.c1 > 2) & (T1.c4.c2 < 3)).run()
        self.assertEqual(len(t1_list), 6)

    def test_internval_nested_queries(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = ((T1.c4.c1 < 4) & (T1.c4.c1 > 1)).run()
        self.assertEqual(len(t1_list), 2)

    def test_in_nested_queries(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = (T1.c4.c1.one_of(1, 2)).run()
        self.assertEqual(len(t1_list), 2)

    def test_sample(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = T1.all().sample(2).run()
        self.assertEqual(len(t1_list), 2)

    def test_base_aggregation(self):
        for c1 in range(0, 5):
            T1(c1='v' + str(c1)).send()
        self.assertEqual(T1.all().max(T1.c1).run(), 'v4')

    def test_nested_aggregation(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        self.assertEqual(T1.all().max(T1.c4.c1).run(), 4)

    def test_complex_aggregation(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        self.assertEqual((T1.c4.c1 > T1.c4.c2).count().run(), 10)


class AsyncTestSkeleton(asynctest.TestCase):

    @classmethod
    def generate_connection_uri(cls):
        return None, {}

    @classmethod
    def setUpClass(cls):
        connection_uri, pool_kwargs = cls.generate_connection_uri()
        if connection_uri is None:
            raise unittest.SkipTest("Skip abstrac class")
        orm_register.init(connection_uri, pool_kwargs, async_mode=True)

    async def setUp(self):
        await orm_register.async_load()

    async def tearDown(self):
        await orm_register.async_strategy.drop_table(T1._table)

    @classmethod
    def tearDownClass(cls):
        asyncio.get_event_loop().run_until_complete(orm_register.async_close())

    async def test_base_interaction(self):
        t1 = T1(c1='5', c2='6')
        t2 = T1(c1='6', c2='7')
        await asyncio.gather(t1.async_send(), t2.async_send())
        t1_list = await T1.all().async_run()
        self.assertEqual(len(t1_list), 2)

    async def test_simple_search(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 10)])
        t1_list = await (T1.c1 > '5').async_run()
        self.assertEqual(len(t1_list), 4)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    async def test_magic_update(self):
        t1_1 = T1(c1='5', c2='6')
        await t1_1.async_send()
        t1_2 = (await T1.all().async_run())[0]
        t1_2.c2 = '7'
        await t1_2.async_send()
        await t1_1.async_load()
        self.assertEqual(t1_1.c2, '7')

    async def test_datetime(self):
        test_datetime = orm_register.current_utc_datetime() + timedelta(minutes=5)
        t1_original = T1(c3=test_datetime)
        await t1_original.async_send()
        t1_1 = (await T1.all().async_run())[0]
        self.assertEqual(t1_1.c3, t1_original.c3)
        t1_2 = (await (T1.c3 == test_datetime).async_run())[0]
        self.assertEqual(t1_2.c3, t1_original.c3)

    async def test_complex_search(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 10)])
        t1_list = await ((T1.c1 > '5') & (T1.c1 < '8')).async_run()
        self.assertEqual(len(t1_list), 2)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    async def test_sotring(self):
        await asyncio.wait([
            T1(c1=str(c1), c2=str(c2)).async_send()
            for c1 in range(0, 3) for c2 in range(0, 3)
        ])
        t1_list = await T1.all().order_by(T1.c1.amount.desc(), T1.c2.amount.desc()).async_run()
        self.assertEqual(t1_list[0].c1, '2')
        self.assertEqual(t1_list[0].c2, '2')

    async def test_nested_queries(self):
        t1 = T1(c4={"c2": 5})
        await t1.async_send()
        t1_search = (await (T1.c4.c2 == 5).async_run())[0]
        self.assertEqual(t1.c4, t1_search.c4)

    async def test_complex_nested_queries(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        t1_list = await ((T1.c4.c1 > 2) & (T1.c4.c2 < 3)).async_run()
        self.assertEqual(len(t1_list), 6)

    async def test_internval_nested_queries(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await ((T1.c4.c1 < 4) & (T1.c4.c1 > 1)).async_run()
        self.assertEqual(len(t1_list), 2)

    async def test_in_nested_queries(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await (T1.c4.c1.one_of(1, 2)).async_run()
        self.assertEqual(len(t1_list), 2)

    async def test_sample(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await T1.all().sample(2).async_run()
        self.assertEqual(len(t1_list), 2)

    async def test_base_aggregation(self):
        await asyncio.wait([T1(c1='v' + str(c1)).async_send() for c1 in range(0, 5)])
        self.assertEqual(await T1.all().max(T1.c1).async_run(), 'v4')

    async def test_nested_aggregation(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        self.assertEqual(await T1.all().max(T1.c4.c1).async_run(), 4)

    async def test_complex_aggregation(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        self.assertEqual(await (T1.c4.c1 > T1.c4.c2).count().async_run(), 10)
