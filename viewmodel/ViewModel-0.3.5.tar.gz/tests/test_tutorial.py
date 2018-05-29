# tests of pymongo interface 
from unittest.mock import MagicMock

from datetime import datetime,date
from decimal import Decimal

from bson.objectid import ObjectId

import pytest
from objdict import (ObjDict, Struct)
from viewmodel.viewFields import (IdField, TxtField, EnumForeignField, IntField,
            DateField, TimeField, Case, DecField,
            viewModelDB, BaseField, IdAutoField )

from viewmodel import DBMongoSource, viewFields, ViewRow

#import saltMongDB
#from sbextend import SaltReq
from viewmodel.viewModel import BaseView

from viewmodel.viewMongoSources import DBMongoSource
import os
import shutil


class Student(BaseView):
    models_ = viewModelDB.default(viewModelDB.baseDB.db.Students)
    id = IdField(cases={}) # , name = '_id')
    name = TxtField()
    course = TxtField(value='engineering')
    course_year = IntField()

    def x__init__(self, *args, **kargs):
        import pdb; pdb.set_trace()
        super().__init__(*args, **kargs)


class StudentObj(BaseView):
    models_ = viewModelDB.default(viewModelDB.baseDB.db.Students)
    id = IdField(cases={}) # , name = '_id')
    first_name = TxtField(src='.name')
    course = TxtField(value='engineering')
    course_year = IntField()


class TestTutorial:
    def test_init_db_tutversion(self):
        name = "Fred Smith"
        student = Student(models=viewModelDB.default('Student2s'))
        assert len(student)== 0
        student.insert_()
        assert student.dbRows_[0]['Student2s'] == {}
        with student:
            student.name = name
        assert student.name == name
        assert student.course == 'engineering'
        assert '_id' in student.dbRows_[0]['Student2s']

    def test_init_db(self):
        student = Student()
        name = "Fred Smith"
        assert len(student)== 0
        student.insert_()
        with student:
            student.name = name
        assert student.name == name

    def test_read_and_modify(self):
        student = Student({})
        assert len(student)==1
        assert student.course_year == None
        assert student.course == 'engineering'

        with student:
            student.course_year = 2
            student.course = 'Computing'

    def test_add_second(self):
        student = Student()
        assert len(student)==0
        student.insert_()
        with student:
            student.name = 'Jane'
            student.course_year = 3
            student.course = 'Computer Engineering'

    def test_read_multiple(self):
        students = Student({})
        assert len(students)==2
        student = students[1]
        assert student.course_year == 3
        with student:
            student.course_year = 2

    def test_read_multiple_dict(self):
        students = Student({'course_year':2})
        assert len(students)==2
        student = students[1]
        assert student.course_year == 2
        for student in students:
            assert student.course_year == 2

    def test_delete_method(self):
        # Prepare
        test_data = Student({})
        original_size = len(test_data)
        to_delete = test_data[0]
        id_to_delete = test_data[0]['id'].value

        # Delete one record
        with to_delete:
            to_delete.delete_()

        # Get the updated data
        after_delete = Student({})

        # Assert the size
        assert len(after_delete) == original_size - 1

        # Assert if the deleted data is gone
        for item in after_delete:
            assert item['id'] != id_to_delete


class TestEmbededViewInContainer:
    def test_in_struct(self):
        tstruct = Struct(student=Student())
        st = str(tstruct)
        assert 'Student' in st

    def test_row_in_struct(self):
        stu_row = Student()[0]
        tstruct = Struct(student=stu_row)
        string = str(tstruct)
        assert '{"student": {}}' in string


class TestObjInside:
    def test_map_change(self):
        """ could do some more of these... like test 2 levels"""
        chng = DBMongoSource.map_change
        assert chng({'abc.def':4})['abc'] == {'def': 4}

    def test_map_change_mult(self):
        """ could do some more of these... like test 2 levels"""
        chng = DBMongoSource.map_change
        changed = chng({'abc.def':4, 'abc.2nd':7})
        assert changed['abc'] == {'def': 4, '2nd':7}

    def test_init(self):
        students = StudentObj()
        assert len(students) == 0
        student = students.insert_()
        assert len(students) == 1
        assert type(student) == ViewRow
        with student:
            student.first_name = 'fred'
            assert students.dbRows_[0]['Students']['name'] == {"first_name": "fred"}
            assert 'name.first_name' in students.changes_[0]['Students']
        pass


class Teachers(Student):
    models_ = viewModelDB.default(viewModelDB.baseDB.db.Teachers)


class TestReUseView:
    def test_via_init(self):
        model = viewModelDB.default(viewModelDB.baseDB.db.Teachers)
        teaches = Student({}, models=model)
        assert len(teaches) == 0
        teach = teaches.insert_()
        with teach:
            teach.name = 'tom'
        pass

    def test_subclass(self):
        teaches = Teachers({})
        assert len(teaches) == 1
        teach = teaches.insert_()
        with teach:
            teach.name = 'bill'
        pass


class TestUpDateNoRead:
    def test_update_status(self):
        students = Student({})
        assert len(students) > 0
        first = students[0]
        sid = str(first.id)
        assert first.course_year == 2
        assert len(sid) > 10
        students = Student()
        newfirst = students.insert_()
        with newfirst:
            newfirst.id = sid
            assert isinstance(newfirst.id, ObjectId) # check setting id via string
            newfirst.course_year = 3
        students = Student({}) # read back
        assert students[0].course_year == 3


@pytest.fixture
def remove_journals():
    def remove():
        folder = TestJournal.journals_folder
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    remove()  # Remove before test
    yield remove()  # Remove after test


class TestJournal:
    journals_folder = os.path.join('..', 'journals')
    journal_file = os.path.join(journals_folder, '_Student.log')

    def test_no_journals_created_after_read(self, remove_journals):
        Student({})
        assert not os.path.isdir(TestJournal.journals_folder)

    def test_no_journals_created_after_deletion(self, remove_journals):
        student = Student({})
        to_delete = student[0]

        with to_delete:
            to_delete.delete_()

        # There should be a folder
        assert os.path.isdir(TestJournal.journals_folder) is False

    def test_default_value_of_should_journal_should_be_False(self):
        assert BaseView.should_journal is False  # Before inherit
        assert Student.should_journal is False  # After inherit

    def test_journal_created_after_update_case1(self, remove_journals):
        Student.should_journal = True
        student = Student({})
        to_change = student[0]

        new_value = "SuperCat"

        with to_change:
            to_change.name = new_value

        # There should be a folder
        assert os.path.isdir(TestJournal.journals_folder)

        # There should be a file in the folder and not empty
        file = TestJournal.journal_file
        assert (os.path.isfile(file) and os.path.getsize(file) > 0)

        # Should be only one line in the file with correct data
        with open(file) as f:
            lines = f.readlines()

        assert lines is not None
        assert len(lines) is 1
        assert datetime.now().strftime('%Y-%m-%d %H:%M') in lines[0]
        assert '[{"Students": {"name": "SuperCat"}}]' in lines[0]

    def test_no_journals_created_after_update_case2(self, remove_journals):
        Student.should_journal = False
        student = Student({})
        to_change = student[0]

        with to_change:
            to_change.name = "SuperCat"

        # There should be no folder
        assert os.path.isdir(TestJournal.journals_folder) is False
