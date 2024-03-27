from live_cells import mutable, batched, computed
from live_cells.stateful_cell import GlobalStateMap

from .util import CountTestObserver, ValueTestObserver

def test_initial_value():
    """Test that the initial value of a mutable cell is the value given in constructor."""

    cell = mutable(15)
    assert cell.value == 15

def test_set_value():
    """Test that setting the value changes the cell's value."""

    cell = mutable(15)

    cell.value = 23
    cell.value = 101

    assert cell.value == 101

def test_notifies_observer(observers):
    """Test that setting the value notifies the observer."""

    cell = mutable(15)
    observer = CountTestObserver()

    observers.add(cell, observer)
    cell.value = 23

    assert observer.count_update == 1

def test_notifies_observers_twice(observers):
    """Test that setting value twice notifies observers twice."""

    cell = mutable(15)
    observer = CountTestObserver()

    observers.add(cell, observer)
    cell.value = 23
    cell.value = 101

    assert observer.count_update == 2

def test_remove_observer(observers):
    """Test that observer not notified after it is removed."""

    cell = mutable(15)
    observer = CountTestObserver()

    observers.add(cell, observer)
    cell.value = 23

    cell.remove_observer(observer)
    cell.value = 101

    assert observer.count_update == 1

def test_new_value_equals_old_value(observers):
    """Test that observers are not called when the new value equals old value."""

    cell = mutable(56)
    observer = CountTestObserver()

    observers.add(cell, observer)
    cell.value = 56

    assert observer.count_update == 0

def test_all_observers_notified(observers):
    """Test that all observers are notified."""

    cell = mutable(3)

    observer1 = CountTestObserver()
    observer2 = CountTestObserver()

    observers.add(cell, observer1)
    cell.value = 5

    observers.add(cell, observer2)
    cell.value = 8
    cell.value = 12

    assert observer1.count_update == 3
    assert observer2.count_update == 2

def test_observed_values(observers):
    """Test that the current value is observed when observers are notified."""

    cell = mutable('hello')
    observer = ValueTestObserver()

    observers.add(cell, observer)

    cell.value = 'hi'
    cell.value = 'bye'

    assert observer.values == ['hi', 'bye']

def test_batch_update(observers):
    """Test that all cells are updated correctly during batch update."""

    a = mutable(0)
    b = mutable(0)
    op = mutable('')

    sum = computed(lambda: a() + b())
    msg = computed(lambda: f'{a()} {op()} {b()} = {sum()}')

    observer = ValueTestObserver()
    observers.add(msg, observer)

    @batched
    def set_cells1():
        a.value = 1
        b.value = 2
        op.value = '+'

    @batched
    def set_cells2():
        a.value = 5
        b.value = 6
        op.value = 'plus'

    set_cells1()
    set_cells2()

    assert observer.values == ['1 + 2 = 3', '5 plus 6 = 11']

def test_compares_equal():
    """Test that two cells compare equal when they have the same keys."""

    a = mutable(0, key = 'mutable-cell-key1')
    b = mutable(0, key = 'mutable-cell-key1')

    assert a == b
    assert hash(a) == hash(b)

def test_compares_not_equal():
    """Test that two cells compare not equal when they have different keys."""

    a = mutable(0, key = 'mutable-cell-key1')
    b = mutable(0, key = 'mutable-cell-key2')

    assert a != b
    assert a == a


def test_compares_not_equal_none_keys():
    """Test that two cells compare not equal when they have None keys."""

    a = mutable(0)
    b = mutable(0)

    assert a != b
    assert a == a

def test_state_sharing(observers):
    """Test that cells with the same key share the same state."""

    a = mutable(0, key = 'mutable-cell-key1')
    b = mutable(0, key = 'mutable-cell-key1')

    observers.observe(a)
    observers.observe(b)

    a.value = 10

    assert a.value == 10
    assert b.value == 10

def test_state_sharing_observers(observers):
    """Test that cells with the same key manage the same set of observers."""

    a = mutable(0, key = 'mutable-cell-key1')
    b = mutable(0, key = 'mutable-cell-key1')

    observers.observe(a)
    observers.observe(b)

    observer1 = ValueTestObserver()
    observer2 = ValueTestObserver()

    observers.add(a, observer1)
    observers.add(b, observer2)

    a.value = 10
    b.value = 20
    a.value = 30
    b.value = 40

    b.remove_observer(observer1)
    a.value = 50

    a.remove_observer(observer2)
    a.value = 60
    b.value = 70

    assert observer1.values == [10, 20, 30, 40]
    assert observer2.values == [10, 20, 30, 40, 50]

def test_no_state_sharing(observers):
    """Test that cells with different keys do not share the same state."""

    a = mutable(0, key = 'mutable-cell-key1')
    b = mutable(0, key = 'mutable-cell-key2')

    observers.observe(a)
    observers.observe(b)

    a.value = 10

    assert a.value == 10
    assert b.value == 0

def test_no_state_sharing_observers(observers):
    """Test that cells with different keys do manage different sets of observers."""

    a = mutable(0, key = 'mutable-cell-key1')
    b = mutable(0, key = 'mutable-cell-key2')

    observers.observe(a)
    observers.observe(b)

    observer1 = ValueTestObserver()
    observer2 = ValueTestObserver()

    observers.add(a, observer1)
    observers.add(b, observer2)

    a.value = 10
    b.value = 20
    a.value = 30
    b.value = 40

    b.remove_observer(observer1)
    a.value = 50

    a.remove_observer(observer2)
    a.value = 60
    b.value = 70

    assert observer1.values == [10, 30, 50, 60]
    assert observer2.values == [20, 40, 70]

def test_state_recreation(observers):
    """Test that the cell state is recreated after disposal."""

    a = mutable(0, key='mutable-cell-key1')

    observer = CountTestObserver()
    observers.add(a, observer)

    assert a.value == 0

    a.value = 10
    a.value = 15

    assert a.value == 15

    a.remove_observer(observer)
    observers.add(a, observer)

    assert a.value == 0

    a.value = 17

    assert a.value == 17

def test_no_leaks(observers):
    """Test that cells with keys do not leak resources."""

    a = mutable(0, key='mutable-cell-key1')
    observer = CountTestObserver()

    observers.add(a, observer)
    assert GlobalStateMap.instance.maybe_get('mutable-cell-key1') is not None

    a.remove_observer(observer)
    assert GlobalStateMap.instance.maybe_get('mutable-cell-key1') is None
