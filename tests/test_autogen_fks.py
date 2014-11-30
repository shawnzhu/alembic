import sys
from alembic.testing import TestBase

from sqlalchemy import MetaData, Column, Table, Integer, String, \
    ForeignKeyConstraint
from alembic.testing import eq_

py3k = sys.version_info >= (3, )

from .test_autogenerate import AutogenFixtureTest


class AutogenerateForeignKeysTest(AutogenFixtureTest, TestBase):
    __only_on__ = 'sqlite'

    def test_extra_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('table', m1,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)))

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              ForeignKeyConstraint(['test2'], ['table.test']))

        Table('table', m2,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)))

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10))
              )

        diffs = self._fixture(m1, m2)

        eq_(diffs[0][0], "drop_fk")
        eq_(diffs[0][2].name, "user")
        eq_(diffs[0][3].constrained_columns, ('test2',))
        eq_(diffs[0][3].referred_table, 'table')
        eq_(diffs[0][3].referred_columns, ('test',))

    def test_missing_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('table', m1,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)))

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)))

        Table('table', m2,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)))

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              ForeignKeyConstraint(['test2'], ['table.test']))

        diffs = self._fixture(m1, m2)

        eq_(diffs[0][0], "add_fk")
        eq_(diffs[0][1].parent.table.name, "user")
        eq_(diffs[0][2].constrained_columns, ('test2',))
        eq_(diffs[0][2].referred_table, 'table')
        eq_(diffs[0][2].referred_columns, ('test',))

    def test_no_change(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('table', m1,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)))

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              ForeignKeyConstraint(['test2'], ['table.test']))

        Table('table', m2,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)))

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              ForeignKeyConstraint(['test2'], ['table.test']))

        diffs = self._fixture(m1, m2)

        eq_(diffs, [])

    def test_no_change_composite_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('table', m1,
              Column('id', Integer, primary_key=True),
              Column('id_1', String(10)),
              Column('id_2', String(10)))

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['table.id_1','table.id_2']))

        Table('table', m2,
              Column('id', Integer, primary_key=True),
              Column('id_1', String(10)),
              Column('id_2', String(10)))

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['table.id_1','table.id_2']))

        diffs = self._fixture(m1, m2)

        eq_(diffs, [])

    def test_missing_composite_fk_with_name(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('table', m1,
              Column('id', Integer, primary_key=True),
              Column('id_1', String(10)),
              Column('id_2', String(10)))

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)))

        Table('table', m2,
              Column('id', Integer, primary_key=True),
              Column('id_1', String(10)),
              Column('id_2', String(10)))

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['table.id_1','table.id_2'],
                                   name='fk_test_name'))

        diffs = self._fixture(m1, m2)

        eq_(diffs[0][0], "add_fk")
        eq_(diffs[0][1].parent.table.name, "user")
        eq_(diffs[0][1].name, "fk_test_name")
        eq_(diffs[0][2].constrained_columns, ('other_id_1', 'other_id_2'))
        eq_(diffs[0][2].referred_table, 'table')
        eq_(diffs[0][2].referred_columns, ('id_1', 'id_2'))

    def test_extra_composite_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('table', m1,
              Column('id', Integer, primary_key=True),
              Column('id_1', String(10)),
              Column('id_2', String(10)))

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['table.id_1', 'table.id_2'],
                                   name='fk_test_name'))

        Table('table', m2,
              Column('id', Integer, primary_key=True),
              Column('id_1', String(10)),
              Column('id_2', String(10)))

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)))

        diffs = self._fixture(m1, m2)

        eq_(diffs[0][0], "drop_fk")
        eq_(diffs[0][2].name, "user")
        eq_(diffs[0][3].constrained_columns, ('other_id_1', 'other_id_2'))
        eq_(diffs[0][3].referred_table, 'table')
        eq_(diffs[0][3].referred_columns, ('id_1', 'id_2'))