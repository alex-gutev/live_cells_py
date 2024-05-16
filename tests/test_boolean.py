import pytest

from live_cells import value, mutable

from .util import ValueTestObserver, observe

class TestBooleanExtension:
    """Tests extension functions on boolean cells."""

    def test_and(self):
        a = mutable(True)
        b = mutable(True)

        c = a.logand(b)

        assert c.value

        a.value = False
        assert not c.value

        b.value = False
        assert not c.value

        a.value = True
        assert not c.value

        b.value = True
        assert c.value

    def test_and_compares_eq_same_cells(self):
        """Test that two cells created with logand are equal if given the same arguments."""

        a = mutable(True)
        b = mutable(True)

        c1 = a.logand(b)
        c2 = a.logand(b)

        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_and_compares_neq_different_cells(self):
        """Test that cells created with logand are not equal if given different arguments."""

        a = mutable(True)
        b = mutable(True)
        c = mutable(True)

        c1 = a.logand(b)
        c2 = b.logand(c)
        c3 = b.logand(a)

        assert c1 == c1
        assert c1 != c2
        assert c1 != c3
        assert c2 != c3

    def test_or(self):
        a = mutable(True)
        b = mutable(True)

        c = a.logor(b)

        assert c.value

        a.value = False
        assert c.value

        b.value = False
        assert not c.value

        a.value = True
        assert c.value

        b.value = True
        assert c.value

    def test_or_compares_eq_same_cells(self):
        """Test that two cells created with logor are equal if given the same arguments."""

        a = mutable(True)
        b = mutable(True)

        c1 = a.logor(b)
        c2 = a.logor(b)

        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_or_compares_neq_different_cells(self):
        """Test that cells created with logor are not equal if given different arguments."""

        a = mutable(True)
        b = mutable(True)
        c = mutable(True)

        c1 = a.logor(b)
        c2 = b.logor(c)
        c3 = b.logor(a)

        assert c1 == c1
        assert c1 != c2
        assert c1 != c3
        assert c2 != c3

    def test_not(self):
        a = mutable(True)
        b = a.lognot()

        assert not b.value

        a.value = False
        assert b.value

    def test_not_compares_eq_same_cells(self):
        """Test that cells created with lognot are equal if given the same argument."""

        a = mutable(True)

        c1 = a.lognot()
        c2 = a.lognot()

        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_not_compares_neq_same_cells(self):
        """Test that cells created with lognot are not equal if given different arguments."""

        a = mutable(True)
        b = mutable(True)

        c1 = a.lognot()
        c2 = b.lognot()

        assert c1 == c1
        assert c1 != c2

    def test_select(self):
        a = value('true')
        b = mutable('false')
        cond = mutable(True)

        c = cond.select(a, b)

        observer = ValueTestObserver()

        with observe(c, observer):
            cond.value = False
            b.value = 'else'
            cond.value = True

            assert observer.values == ['false', 'else', 'true']

    def test_select_no_else(self):
        a = mutable('true')
        cond = mutable(True)

        b = cond.select(a)

        observer = ValueTestObserver()

        with observe(b, observer):
            cond.value = False
            assert b.value == 'true'

            a.value = 'then'
            assert b.value == 'true'

            cond.value = True
            assert b.value == 'then'

            a.value = 'when'
            assert b.value == 'when'
