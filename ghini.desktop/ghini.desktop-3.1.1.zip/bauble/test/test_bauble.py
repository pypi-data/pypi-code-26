# -*- coding: utf-8 -*-
#
# Copyright (c) 2005,2006,2007,2008,2009 Brett Adams <brett@belizebotanic.org>
# Copyright (c) 2012-2015 Mario Frasca <mario@anche.no>
#
# This file is part of ghini.desktop.
#
# ghini.desktop is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ghini.desktop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ghini.desktop. If not, see <http://www.gnu.org/licenses/>.
#
# test_bauble.py
#
import datetime
import os
import time

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from sqlalchemy import (
    Column, Integer)

import unittest
import bauble
import bauble.db as db
from bauble.btypes import Enum, EnumError
from bauble.test import BaubleTestCase, check_dupids
import bauble.meta as meta

"""Tests for the main bauble module.

don't please give docstrings to tests, better make sure they have a
meaningful name.  docstrings complicate the debugging task of finding back
which function is being invoked.

"""


class EnumTests(BaubleTestCase):

    table = None

    def setUp(self):
        BaubleTestCase.setUp(self)
        if self.__class__.table is None:
            class Test(db.Base):
                __tablename__ = 'test_enum_type'
                id = Column(Integer, primary_key=True)
                value = Column(Enum(values=['1', '2', '']), default='')
            self.__class__.Test = Test
            self.__class__.table = Test.__table__
            self.table.create(bind=db.engine)

    def tearDown(self):
        BaubleTestCase.tearDown(self)

    def test_insert_low_level(self):
        db.engine.execute(self.table.insert(), {"id": 1})

    def test_insert_alchemic(self):
        t = self.Test(id=1)
        self.session.add(t)
        self.session.flush()

    def test_insert_by_value_ok(self):
        t = self.Test(value='1')
        self.session.add(t)
        self.session.flush()

    def test_insert_by_value_wrong_value_seen_late(self):
        from sqlalchemy.exc import StatementError
        t = self.Test(value='33')
        self.session.add(t)
        self.assertRaises(StatementError, self.session.flush)

    def function_creating_enum(self, name, values, **kwargs):
        self.Table = type(
            'test_table_' + name, (db.Base, ),
            {'__tablename__': 'test_enum_type_' + name,
             'id': Column(Integer, primary_key=True),
             'value': Column(Enum(values=values, **kwargs), default=''),
             })
        self.table = self.Table.__table__
        self.table.create(bind=db.engine)

    def test_bad_enum(self):
        self.function_creating_enum('zero', ['1', '2', '3', ])
        self.assertRaises(EnumError, self.function_creating_enum, 'one', [])
        self.assertRaises(EnumError, self.function_creating_enum, 'two', None)
        self.assertRaises(EnumError, self.function_creating_enum, 'three',
                          [1, ''])  # int can't be
        self.assertRaises(EnumError, self.function_creating_enum, 'four',
                          ['1', '1', ])  # same value twice
        self.assertRaises(EnumError, self.function_creating_enum, 'five',
                          ['1', [], None])  # strings please
        self.assertRaises(EnumError, self.function_creating_enum, 'six',
                          ['1', '2'], empty_to_none=True)  # no empty

    def test_empty_to_none(self):
        self.function_creating_enum('seven', ['1', None], empty_to_none=True)
        t = self.Table(value='1')
        self.session.add(t)
        t = self.Table(value='')
        self.session.add(t)
        self.session.flush()
        q = self.session.query(self.Table).filter_by(value='')
        self.assertEqual(q.all(), [])
        q = self.session.query(self.Table).filter_by(value=None)
        self.assertEqual(q.all(), [t])


class BaubleTests(BaubleTestCase):
    def test_date_type(self):
        dt = bauble.btypes.Date()

        bauble.btypes.Date._dayfirst = False
        bauble.btypes.Date._yearfirst = False
        s = '12-30-2008'
        v = dt.process_bind_param(s, None)
        self.assertTrue(v.month == 12 and v.day == 30 and v.year == 2008,
                     '%s == %s' % (v, s))

        bauble.btypes.Date._dayfirst = True
        bauble.btypes.Date._yearfirst = False
        s = '30-12-2008'
        v = dt.process_bind_param(s, None)
        self.assertTrue(v.month == 12 and v.day == 30 and v.year == 2008,
                     '%s == %s' % (v, s))

        bauble.btypes.Date._dayfirst = False
        bauble.btypes.Date._yearfirst = True
        s = '2008-12-30'
        v = dt.process_bind_param(s, None)
        self.assertTrue(v.month == 12 and v.day == 30 and v.year == 2008,
                     '%s == %s' % (v, s))

    def test_datetime_type(self):
        dt = bauble.btypes.DateTime()

        # with negative timezone
        s = '2008-12-1 11:50:01.001-05:00'
        expect = '2008-12-01 11:50:01.001000-05:00'
        result = dt.process_bind_param(s, None)
        self.assertEquals(str(result), expect)

        # test with positive timezone
        s = '2008-12-1 11:50:01.001+05:00'
        result = '2008-12-01 11:50:01.001000+05:00'
        v = dt.process_bind_param(s, None)
        self.assertTrue(str(v) == result, '%s == %s' % (v, result))

        # test with no timezone
        s = '2008-12-1 11:50:01.001'
        result = '2008-12-01 11:50:01.001000'
        v = dt.process_bind_param(s, None)
        self.assertTrue(str(v) == result, '%s == %s' % (v, result))

        # test with no milliseconds
        s = '2008-12-1 11:50:01'
        result = '2008-12-01 11:50:01'
        v = dt.process_bind_param(s, None)
        self.assertTrue(v.isoformat(' ') == result)

    def test_base_table(self):

        m = meta.BaubleMeta(name='name', value='value')
        self.session.add(m)
        self.session.commit()
        m = self.session.query(meta.BaubleMeta).filter_by(name='name').first()

        # test that _created and _last_updated were created correctly
        self.assertTrue(hasattr(m, '_created')
                     and isinstance(m._created, datetime.datetime))
        self.assertTrue(hasattr(m, '_last_updated')
                     and isinstance(m._last_updated, datetime.datetime))

        # test that created does not change when the value is updated
        # but that last_updated does
        created = m._created
        last_updated = m._last_updated
        # sleep for one second before committing since the DateTime
        # column only has one second granularity
        time.sleep(1.1)
        m.value = 'value2'
        self.session.commit()
        self.session.expire(m)
        self.assertTrue(isinstance(m._created, datetime.datetime))
        self.assertTrue(m._created == created)
        self.assertTrue(isinstance(m._last_updated, datetime.datetime))
        self.assertTrue(m._last_updated != last_updated)

    def test_duplicate_ids(self):
        import bauble as mod
        import glob
        head, tail = os.path.split(mod.__file__)
        files = glob.glob(os.path.join(head, '*.glade'))
        for f in files:
            ids = check_dupids(f)
            self.assertTrue(ids == [], "%s has duplicate ids: %s" % (f, str(ids)))


class HistoryTests(BaubleTestCase):

    def test(self):
        from bauble.plugins.plants import Family
        f = Family(family='Family')
        self.session.add(f)
        self.session.commit()
        history = self.session.query(db.History).\
            order_by(db.History.timestamp.desc()).first()
        assert history.table_name == 'family' and history.operation == 'insert'

        f.family = 'Family2'
        self.session.commit()
        history = self.session.query(db.History).\
            order_by(db.History.timestamp.desc()).first()
        assert history.table_name == 'family' and history.operation == 'update'

        self.session.delete(f)
        self.session.commit()
        history = self.session.query(db.History).\
            order_by(db.History.timestamp.desc()).first()
        assert history.table_name == 'family' and history.operation == 'delete'


class MVPTests(BaubleTestCase):

    def test_can_programmatically_connect_signals(self):
        from bauble.editor import (
            GenericEditorPresenter, GenericEditorView)

        class HandlerDefiningPresenter(GenericEditorPresenter):
            def on_tag_desc_textbuffer_changed(self, *args):
                pass

        model = db.History()
        import tempfile
        ntf = tempfile.NamedTemporaryFile(mode='w+')
        ntf.write('''\
<interface>
  <requires lib="gtk+" version="2.24"/>
  <!-- interface-naming-policy toplevel-contextual -->
  <object class="GtkDialog" id="handler-defining-view"/>
</interface>
''')
        ntf.flush()
        fn = ntf.name
        view = GenericEditorView(fn, None, 'handler-defining-view')
        presenter = HandlerDefiningPresenter(model, view)
        natural_number_for_dialog_box = len(presenter.view._GenericEditorView__attached_signals)
        ntf = tempfile.NamedTemporaryFile(mode='w+')
        ntf.write('''\
<interface>
  <requires lib="gtk+" version="2.24"/>
  <!-- interface-naming-policy toplevel-contextual -->
  <object class="GtkTextBuffer" id="tag_desc_textbuffer">
    <signal name="changed" handler="on_tag_desc_textbuffer_changed" swapped="no"/>
  </object>
  <object class="GtkDialog" id="handler-defining-view"/>
</interface>
''')
        ntf.flush()
        fn = ntf.name
        view = GenericEditorView(fn, None, 'handler-defining-view')
        presenter = HandlerDefiningPresenter(model, view)
        self.assertEqual(
            len(presenter.view._GenericEditorView__attached_signals), natural_number_for_dialog_box + 1)
        presenter.on_tag_desc_textbuffer_changed()  # avoid uncounted line!


class GlobalFunctionsTests(unittest.TestCase):
    def test_newer_version_on_github(self):
        import io
        from bauble.connmgr import newer_version_on_github
        stream = io.StringIO('version = "1.0.0"  # comment')
        self.assertFalse(newer_version_on_github(stream) and True or False)
        stream = io.StringIO('version = "1.0.99999"  # comment')
        self.assertTrue(newer_version_on_github(stream) and True or False)
        stream = io.StringIO('version = "1.0.99999"  # comment')
        self.assertEqual(newer_version_on_github(stream), '1.0.99999')
        stream = io.StringIO('version = "1.099999"  # comment')
        self.assertFalse(newer_version_on_github(stream) and True or False)
        stream = io.StringIO('version = "1.0.99999-dev"  # comment')
        self.assertFalse(newer_version_on_github(stream) and True or False)
