import pytest

from live_cells import value, mutable, computed
from .util import ValueTestObserver, observe, MockException

class TestErrorHandlingExtension:
    """Tests error handling cell extension methods."""

    def test_on_error(self):
        """Test on_error method without exception type argument."""

        a = mutable(1)

        @computed
        def b():
            if a() <= 0:
                raise Exception('A generic exception')

            return a()

        c = mutable(2)
        result = b.on_error(c)

        observer = ValueTestObserver()

        with observe(result, observer):
            assert result.value == 1

            a.value = 0
            c.value = 4
            a.value = 10
            c.value = 100

            assert observer.values == [2, 4, 10]

    def test_on_error_with_type(self):
        """Test on_error method with exception type argument."""

        a = mutable(1)

        @computed
        def b():
            if a() < 0:
                raise Exception('A generic exception')

            elif a() == 0:
                raise MockException

            return a()

        c = mutable(2)
        result = b.on_error(c, type=MockException)

        observer = ValueTestObserver()

        with observe(result, observer):
            assert result.value == 1

            a.value = 0
            c.value = 4
            a.value = 10
            c.value = 100

            assert observer.values == [2, 4, 10]

            with pytest.raises(Exception):
                a.value = -1
                result.value

    def test_on_error_compares_equal_same_cells_and_type(self):
        """Test that cells created with on_error compare == for the same arguments."""

        a = mutable(0)
        e1 = a.on_error(value(-1))
        e2 = a.on_error(value(-1))

        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_on_error_compares_not_equal_different_self_cell(self):
        """Test that cells created with on_error compare != when called on different self cells."""

        a = mutable(0)
        b = mutable(0)

        e1 = a.on_error(value(-1))
        e2 = b.on_error(value(-1))

        assert e1 != e2
        assert e1 == e1

    def test_on_error_compares_not_equal_different_value_cell(self):
        """Test that cells created with on_error compare != when given different value cell."""

        a = mutable(0)

        e1 = a.on_error(value(-1))
        e2 = a.on_error(value(-2))

        assert e1 != e2
        assert e1 == e1

    def test_on_error_compares_not_equal_different_type(self):
        """Test that cells created with on_error compare != when given a different exception type."""

        a = mutable(0)

        e1 = a.on_error(value(-1))
        e2 = a.on_error(value(-1), type=MockException)
        e3 = a.on_error(value(-1), type=MockException)

        assert e1 != e2
        assert e1 != e3
        assert e2 == e3

    def test_error(self):
        """Test error() method."""

        a = mutable(1)

        @computed
        def b():
            if a() < 0:
                raise MockException

            return a()

        error = b.error()

        observer = ValueTestObserver()

        with observe(error, observer):
            assert error.value is None

            a.value = 2
            assert error.value is None

            a.value = -1
            assert isinstance(error.value, MockException)

            a.value = 3
            assert isinstance(error.value, MockException)

    def test_error_all_true(self):
        """Test that error(all=True) updates to None when no error."""

        a = mutable(1)

        @computed
        def b():
            if a() < 0:
                raise MockException

            return a()

        error = b.error(all=True)

        observer = ValueTestObserver()

        with observe(error, observer):
            assert error.value is None

            a.value = 2
            assert error.value is None

            a.value = -1
            assert isinstance(error.value, MockException)

            a.value = 3
            assert error.value is None

    def test_error_with_type(self):
        """Test error() method with exception type argument."""

        a = mutable(1)

        @computed
        def b():
            if a() < 0:
                raise Exception('A generic exception')

            elif a() == 0:
                raise MockException

            return a()

        error = b.error(type=MockException)

        with observe(error, ValueTestObserver()):
            assert error.value is None

            a.value = 2
            assert error.value is None

            a.value = 0
            assert isinstance(error.value, MockException)

            a.value = 3;
            assert isinstance(error.value, MockException)

            a.value = -1
            assert isinstance(error.value, MockException)


    def test_error_with_type_all_true(self):
        """Test error(all=True) method with exception type argument."""

        a = mutable(1)

        @computed
        def b():
            if a() < 0:
                raise Exception('A generic exception')

            elif a() == 0:
                raise MockException

            return a()

        error = b.error(all=True, type=MockException)

        with observe(error, ValueTestObserver()):
            assert error.value is None

            a.value = 2
            assert error.value is None

            a.value = 0
            assert isinstance(error.value, MockException)

            a.value = -1
            assert error.value is None

    def test_error_compares_equal_with_same_cell(self):
        """Test that cells created with error() compare == for the same cell arguments."""

        a = mutable(0)

        e1 = a.error()
        e2 = a.error()

        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_error_compares_equal_with_same_cell_and_type(self):
        """Test that cells created with error() compare == for the same cell and type arguments."""

        a = mutable(0)

        e1 = a.error(type=MockException)
        e2 = a.error(type=MockException)

        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_error_compares_not_equal_with_different_cells(self):
        """Test that cells created with error() compare != when given different cell arguments."""

        a = mutable(0)
        b = mutable(0)

        e1 = a.error()
        e2 = b.error()

        assert e1 != e2
        assert e1 == e1

    def test_error_compares_not_equal_with_different_types(self):
        """Test that cells created with error() compare != when given different type arguments."""

        a = mutable(0)

        e1 = a.error()
        e2 = a.error(type=MockException)

        assert e1 != e2
        assert e1 == e1

    def test_error_compares_not_equal_with_different_arguments(self):
        """Test that cells created with error() compare != when all arguments are different."""

        a = mutable(0)

        e1 = a.error(all=True)
        e2 = a.error(all=False)
        e3 = a.error(all=True)

        assert e1 != e2
        assert e1 == e1
        assert e1 == e3
