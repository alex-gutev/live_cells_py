import pytest

from live_cells import value, mutable, computed, none
from util import (
    observe,
    CountTestObserver, ValueTestObserver,
    MockException,
    LifecycleCounter, LifecycleTestCell
)

class TestDynamicComputedCell:
    """Tests the behaviour of a computed cell that discovers its dependencies at runtime."""

    def test_function_on_constant(self):
        """Test a basic function applied on a constant cell."""

        a = value(1)
        b = computed(lambda: a() + 1)

        assert b.value == 2

    def test_recompute_on_argument_change(self):
        """Test that computed cell is recomputed when argument values change."""

        a = mutable(1)
        b = computed(lambda: a() + 1)

        observer = ValueTestObserver()

        with observe(b, observer):
            a.value = 5
            a.value = 10

            assert observer.values == [6, 11]

    def test_recompute_when_all_argument_change(self):
        """Test that the cell is recomputed when all the arguments change."""

        a = mutable(1)
        b = mutable(1)

        c = computed(lambda: a() + b())

        observer = ValueTestObserver()

        with observe(c, observer):
            a.value = 5
            b.value = 8
            a.value = 100

            assert observer.values == [6, 13, 108]

    def test_observer_removal(self):
        """Test that the observer is not called after it is removed."""

        a = mutable(1)
        b = mutable(2)

        c = computed(lambda: a() + b())

        observer = ValueTestObserver()

        with observe(c, observer):
            a.value = 8
            b.value = 10

        a.value = 100
        b.value = 1000

        assert observer.values == [10, 18]

    def test_all_observers_notified(self):
        """Test that all observers are notified when value changes."""

        a = mutable(1)
        b = mutable(2)

        c = computed(lambda: a() + b())

        observer1 = ValueTestObserver()
        observer2 = ValueTestObserver()

        with observe(c, observer1):
            a.value = 8

            with observe(c, observer2):
                b.value = 10
                a.value = 100

                assert observer1.values == [10, 18, 110]
                assert observer2.values == [18, 110]

    def test_argument_tracking_in_conditionals(self):
        """Test that arguments are tracked correctly when appearing in conditionals."""

        a = mutable(True)
        b = mutable(2)
        c = mutable(3)

        d = computed(lambda: b() if a() else c())

        observer = ValueTestObserver()

        with observe(d, observer):
            b.value = 1
            a.value = False
            c.value = 10

            assert observer.values == [1, 3, 10]

    def test_none_preserves_previous_value(self):
        """Test that the previous value is preserved when none() is used."""

        a = mutable(0)
        evens = computed(lambda: a() if a() % 2 == 0 else none())

        observer = ValueTestObserver()

        with observe(evens, observer):
            a.value = 1
            a.value = 2
            a.value = 3
            a.value = 4
            a.value = 5

        assert observer.values == [0, 2, 4]

    def test_cell_initialized_to_none_default_value(self):
        """Test that the value of the cell is initialized to the default value given in none()."""

        a = mutable(1)
        evens = computed(lambda: a() if a() % 2 == 0 else none(0))

        observer = ValueTestObserver()

        with observe(evens, observer):
            a.value = 3
            a.value = 4
            a.value = 5
            a.value = 6

        assert observer.values == [0, 4, 6]

    def test_cell_initialize_to_none_when_no_default_value(self):
        """Test that the value of the cell is initialized to None when no default value given in none()."""

        a = mutable(1)
        evens = computed(lambda: a() if a() % 2 == 0 else none())

        observer = ValueTestObserver()

        with observe(evens, observer):
            a.value = 3
            a.value = 4
            a.value = 5
            a.value = 6

        assert observer.values == [None, 4, 6]



    def test_computed_cell_argument(self):
        """Test that computed cell argument is tracked correctly."""

        a = mutable(True)
        b = mutable(2)
        c = mutable(3)

        d = computed(lambda: b() if a() else c())
        e = mutable(0)
        f = computed(lambda: d() + e())

        observer = ValueTestObserver()

        with observe(f, observer):
            b.value = 1
            e.value = 10
            a.value = False
            c.value = 10

            assert observer.values == [1, 11, 13, 20]

    def test_exception_on_init(self):
        """Test that exceptions in initial value are reproduced on access.

        This also tests the `computed` decorator.

        """

        @computed
        def cell():
            raise MockException

        with pytest.raises(MockException):
            cell.value

    def test_exception_while_observed(self):
        """Test that exceptions are reproduced while being observed."""

        @computed
        def cell():
            raise MockException

        with observe(cell):
            with pytest.raises(MockException):
                cell.value

    def test_compares_equal(self):
        """Test that two cells with the same keys compare equal."""

        a = mutable(0)
        b = mutable(0)

        c1 = computed(lambda: a() + b(), key='theKey')
        c2 = computed(lambda: a() + b(), key='theKey')

        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_compares_not_equal(self):
        """Test that two cells with different keys compare not equal."""

        a = mutable(0)
        b = mutable(0)

        c1 = computed(lambda: a() + b(), key='theKey1')
        c2 = computed(lambda: a() + b(), key='theKey2')

        assert c1 != c2
        assert c1 == c1

    def test_compares_not_equal_none_keys(self):
        """Test that two cells with None keys compare not equal."""

        a = mutable(0)
        b = mutable(0)

        c1 = computed(lambda: a() + b())
        c2 = computed(lambda: a() + b())

        assert c1 != c2
        assert c1 == c1

    def test_compares_equal_decorator(self):
        """Test that two cells with the same keys, defined with @computed, compare equal."""

        a = mutable(0)
        b = mutable(0)

        @computed(key='theKey')
        def c1():
            return a() + b()

        @computed(key='theKey')
        def c2():
            return a() + b()

        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_compares_not_equal_decorator(self):
        """Test that two cells with different keys, defined with @computed, compare not equal."""

        a = mutable(0)
        b = mutable(0)

        @computed(key='theKey1')
        def c1():
            return a() + b()

        @computed(key='theKey2')
        def c2():
            return a() + b()

        assert c1 != c2
        assert c1 == c1

    def test_compares_not_equal_none_keys_decorator(self):
        """Test that two cells with None keys, defined with @computed, compare not equal."""

        a = mutable(0)
        b = mutable(0)

        @computed
        def c1():
            return a() + b()

        @computed
        def c2():
            return a() + b()

        assert c1 != c2
        assert c1 == c1

    def test_shared_state(self):
        """Test that cells with the same keys manage the same observers."""

        counter = LifecycleCounter()
        a = LifecycleTestCell(0, counter)

        def f():
            return computed(lambda: a() + 1, key='theKey')

        assert counter.count_init == 0

        observer = CountTestObserver()

        with observe(f(), observer):
            assert counter.count_init == 1
            assert counter.count_dispose == 0

            f().remove_observer(observer)

            assert counter.count_init == 1
            assert counter.count_dispose == 1

    def test_state_recreated(self):
        """Test that the cell's state is recreated after it is destroyed."""

        counter = LifecycleCounter()
        a = LifecycleTestCell(0, counter)

        def f():
            return computed(lambda: a() + 1, key='theKey')

        observer = CountTestObserver()

        with observe(f(), observer):
            f().remove_observer(observer)

        with observe(f()):
            assert counter.count_init == 2
            assert counter.count_dispose == 1
