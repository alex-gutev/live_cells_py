import pytest

from live_cells import value, mutable, computed, computed_cell
from .util import (
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

    def test_recompute_on_argument_change(self, observers):
        """Test that computed cell is recomputed when argument values change."""

        a = mutable(1)
        b = computed(lambda: a() + 1)

        observer = ValueTestObserver()
        observers.add(b, observer)

        a.value = 5
        a.value = 10

        assert observer.values == [6, 11]

    def test_recompute_when_all_argument_change(self, observers):
        """Test that the cell is recomputed when all the arguments change."""

        a = mutable(1)
        b = mutable(1)

        c = computed(lambda: a() + b())

        observer = ValueTestObserver()
        observers.add(c, observer)

        a.value = 5
        b.value = 8
        a.value = 100

        assert observer.values == [6, 13, 108]

    def test_observer_removal(self, observers):
        """Test that the observer is not called after it is removed."""

        a = mutable(1)
        b = mutable(2)

        c = computed(lambda: a() + b())

        observer = ValueTestObserver()
        observers.add(c, observer)

        a.value = 8
        b.value = 10

        c.remove_observer(observer)
        a.value = 100
        b.value = 1000

        assert observer.values == [10, 18]

    def test_all_observers_notified(self, observers):
        """Test that all observers are notified when value changes."""

        a = mutable(1)
        b = mutable(2)

        c = computed(lambda: a() + b())

        observer1 = ValueTestObserver()
        observer2 = ValueTestObserver()

        observers.add(c, observer1)
        a.value = 8

        observers.add(c, observer2)
        b.value = 10
        a.value = 100

        assert observer1.values == [10, 18, 110]
        assert observer2.values == [18, 110]

    def test_argument_tracking_in_conditionals(self, observers):
        """Test that arguments are tracked correctly when appearing in conditionals."""

        a = mutable(True)
        b = mutable(2)
        c = mutable(3)

        d = computed(lambda: b() if a() else c())

        observer = ValueTestObserver()
        observers.add(d, observer)

        b.value = 1
        a.value = False
        c.value = 10

        assert observer.values == [1, 3, 10]

    def test_computed_cell_argument(self, observers):
        """Test that computed cell argument is tracked correctly."""

        a = mutable(True)
        b = mutable(2)
        c = mutable(3)

        d = computed(lambda: b() if a() else c())
        e = mutable(0)
        f = computed(lambda: d() + e())

        observer = ValueTestObserver()
        observers.add(f, observer)

        b.value = 1
        e.value = 10
        a.value = False
        c.value = 10

        assert observer.values == [1, 11, 13, 20]

    def test_exception_on_init(self, observers):
        """Test that exceptions in initial value are reproduced on access.

        This also tests the `computed_cell` decorator.

        """

        @computed_cell()
        def cell():
            raise MockException

        with pytest.raises(MockException):
            cell.value

    def test_exception_while_observed(self, observers):
        """Test that exceptions are reproduced while being observed."""

        @computed_cell()
        def cell():
            raise MockException

        observers.observe(cell)

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
        """Test that two cells with the same keys, defined with @computed_cell(), compare equal."""

        a = mutable(0)
        b = mutable(0)

        @computed_cell(key='theKey')
        def c1():
            return a() + b()

        @computed_cell(key='theKey')
        def c2():
            return a() + b()

        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_compares_not_equal_decorator(self):
        """Test that two cells with different keys, defined with @computed_cell(), compare not equal."""

        a = mutable(0)
        b = mutable(0)

        @computed_cell(key='theKey1')
        def c1():
            return a() + b()

        @computed_cell(key='theKey2')
        def c2():
            return a() + b()

        assert c1 != c2
        assert c1 == c1

    def test_compares_not_equal_none_keys_decorator(self):
        """Test that two cells with None keys, defined with @computed_cell(), compare not equal."""

        a = mutable(0)
        b = mutable(0)

        @computed_cell()
        def c1():
            return a() + b()

        @computed_cell()
        def c2():
            return a() + b()

        assert c1 != c2
        assert c1 == c1

    def test_shared_state(self, observers):
        """Test that cells with the same keys manage the same observers."""

        counter = LifecycleCounter()
        a = LifecycleTestCell(0, counter)

        def f():
            return computed(lambda: a() + 1, key='theKey')

        assert counter.count_init == 0

        observer = CountTestObserver()
        observers.add(f(), observer)

        assert counter.count_init == 1
        assert counter.count_dispose == 0

        f().remove_observer(observer)

        assert counter.count_init == 1
        assert counter.count_dispose == 1

    def test_state_recreated(self, observers):
        """Test that the cell's state is recreated after it is destroyed."""

        counter = LifecycleCounter()
        a = LifecycleTestCell(0, counter)

        def f():
            return computed(lambda: a() + 1, key='theKey')

        observer = CountTestObserver()
        observers.add(f(), observer)

        f().remove_observer(observer)

        observers.observe(f())

        assert counter.count_init == 2
        assert counter.count_dispose == 1
