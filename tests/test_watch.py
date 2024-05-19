from live_cells import watch, mutable, batch, computed
from .util import LifecycleCounter, LifecycleTestCell, ValueTestObserver, observe

class WatchTracker:
    def __init__(self):
        self.values = []

    def add(self, value):
        self.values.append(value)

class TestCellWatcher:
    """Test cell watch functions defined with `watch`"""

    def test_init(self, test_watch):
        """Test that watch function is called on initialization."""

        a = mutable(1)
        b = mutable(2)

        track = WatchTracker()

        @test_watch
        def watch_sum():
            track.add((a(), b()))

        assert track.values == [(1,2)]

    def test_called_on_change(self, test_watch):
        """Test that the watch function is called when cell values change."""

        a = mutable(1)
        b = mutable(2)

        track = WatchTracker()

        @test_watch
        def watch_sum():
            track.add((a(), b()))

        a.value = 5
        b.value = 10

        assert track.values == [(1,2), (5,2), (5,10)]

    def test_called_during_batch(self, test_watch):
        """Test that the watch function is called correctly during a batch update."""

        a = mutable(1)
        b = mutable(2)

        track = WatchTracker()

        @test_watch
        def watch_sum():
            track.add((a(), b()))

        with batch():
            a.value = 5
            b.value = 10

        assert track.values == [(1,2), (5,10)]

    def test_tracks_conditional_arguments(self, test_watch):
        """Test that cells referenced conditionally are tracked correctly."""

        a = mutable(1)
        b = mutable(10)
        select = mutable(True)

        track = WatchTracker()

        @test_watch
        def watcher():
            if select():
                track.add(a())

            else:
                track.add(b())

        a.value = 2
        select.value = False
        b.value = 5

        assert track.values == [1, 2, 10, 5]

    def test_stop(self, test_watch):
        """Test that a watch function is stopped when stop() is called."""

        a = mutable(1)
        b = mutable(2)

        track = WatchTracker()

        @test_watch
        def watcher():
            track.add((a(), b()))

        a.value = 5
        b.value = 10

        watcher.stop()

        b.value = 100
        a.value = 30

        assert track.values == [(1,2), (5,2), (5,10)]

    def test_cell_state_init(self, test_watch):
        """Test that init is called on the watched cell's state."""

        counter = LifecycleCounter()
        cell = LifecycleTestCell(1, counter)

        track = WatchTracker()

        @test_watch
        def watcher():
            track.add(cell())

        assert counter.count_init == 1
        assert counter.count_dispose == 0

    def test_cell_state_dispose(self, test_watch):
        """Test that dispose is called on the watched cell's state when watcher is stopped."""

        counter = LifecycleCounter()
        cell = LifecycleTestCell(1, counter)

        track = WatchTracker()

        @test_watch
        def watcher():
            track.add(cell())

        watcher.stop()

        assert counter.count_init == 1
        assert counter.count_dispose == 1


    def test_cell_state_dispose_not_called(self, test_watch):
        """Test that dispose is not called when not all watchers have been stopped."""

        counter = LifecycleCounter()
        cell = LifecycleTestCell(1, counter)

        track = WatchTracker()

        @test_watch
        def watcher1():
            track.add(cell())

        @test_watch
        def watcher2():
            track.add(cell())

        watcher1.stop()

        assert counter.count_init == 1
        assert counter.count_dispose == 0

    def test_schedule(self, test_watch):
        """Test watch function scheduling."""

        a = mutable(0)
        b = mutable(1)

        calls = []
        first = True

        def schedule(f):
            nonlocal first

            if first:
                first = False
                f()

            else:
                calls.append(f)

        @test_watch(schedule = schedule)
        def watch_ab():
            return (a(), b())

        a.value = 5
        b.value = 10

        a.value = 23
        b.value = 33

        assert len(calls) == 4

        assert calls[0]() == (5, 1)
        assert calls[1]() == (5, 10)
        assert calls[2]() == (23, 10)
        assert calls[3]() == (23, 33)


class TestChangesOnly:
    """Test the changesOnly option"""

    def test_watch_not_called_when_value_unchanged(self, test_watch):
        """Test that the watch function is not called when the value has not changed."""

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)

        track = WatchTracker()

        @test_watch
        def watch_b():
            track.add(b())

        a.value = [4, 2, 6]

        assert track.values == [2]

    def test_watch_not_called_when_value_unchanged_in_batch(self, test_watch):
        """Test that the watch function is not called when the value has not changed with batch()."""

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)

        track = WatchTracker()

        @test_watch
        def watch_b():
            track.add(b())

        with batch():
            a.value = [4, 2, 6]

        assert track.values == [2]

    def test_watch_called_when_value_changed_after_not_changing(self, test_watch):
        """Test that the watch function is called when the value has changed.

        This tests value changes that happen after a value change
        which did not result in the value of the cell actually
        changing.

        """

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)

        track = WatchTracker()

        @test_watch
        def watch_b():
            track.add(b())

        a.value = [4, 2, 6]
        a.value = [7, 8, 9]

        assert track.values == [2, 8]

    def test_watch_called_when_one_argument_changes(self, test_watch):
        """Test that the watch function is called when at least one argument changes."""

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)

        c = mutable(3)

        track = WatchTracker()

        @test_watch
        def watch_b_c():
            track.add((b(), c()))

        with batch():
            a.value = [4, 2, 6]
            c.value = 5

        assert track.values == [(2, 3), (2, 5)]

    def test_computed_cell_not_recomputed_when_arguments_not_changed(self, test_watch):
        """Test that the value of a computed cell is not recomputed when none of the arguments change."""

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)
        c = computed(lambda: b() * 10)

        track = WatchTracker()

        @test_watch
        def watch_c():
            track.add(c())

        a.value = [4, 2, 6]

        assert track.values == [20]

    def test_computed_cell_not_recomputed_when_arguments_not_changed_in_batch(self, test_watch):
        """Test that the value of a computed cell is not recomputed when none of the arguments change in batch()."""

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)
        c = computed(lambda: b() * 10)

        track = WatchTracker()

        @test_watch
        def watch_c():
            track.add(c())

        with batch():
            a.value = [4, 2, 6]

        assert track.values == [20]

    def test_computed_cell_recomputed_when_arguments_change(self, test_watch):
        """Test that the value of a computed cell is recomputed when the arguments change.

        This tests that the computed cell is recomputed when the
        values of the arguments change AFTER they having not changed
        during the previous update cycle.

        """

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)
        c = computed(lambda: b() * 10)

        track = WatchTracker()

        @test_watch
        def watch_c():
            track.add(c())

        a.value = [4, 2, 6]
        a.value = [7, 8, 9]

        assert track.values == [20, 80]

    def test_computed_cell_recomputed_when_one_argument_changes(self, test_watch):
        """Test that the value of a computed cell is recomputed when the only one argument changes."""

        a = mutable([1, 2, 3])
        b = computed(lambda: a()[1], changes_only=True)

        c = mutable(3)
        d = computed(lambda: b() * c())

        track = WatchTracker()

        @test_watch
        def watch_d():
            track.add(d())

        with batch():
            a.value = [4, 2, 6]
            c.value = 5

        assert track.values == [6, 10]

class TestPeekCell:
    """Test peeking cell values."""

    def test_peek_value_equals_cell_value(self):
        """Test that the value of a peek cell equals the value of the original cell."""

        cell = mutable(0)
        peek = cell.peek

        assert peek.value == 0

        cell.value = 2
        assert peek.value == 2

    def test_peek_does_not_notify_observers(self):
        """Test that peek cells do not notify their observers."""

        a = mutable(0)
        b = mutable(1)

        sum = computed(lambda: a.peek() + b())

        with observe(sum, ValueTestObserver()) as observer:
            a.value = 1
            a.value = 2
            a.value = 3
            b.value = 5
            b.value = 10
            a.value = 2
            b.value = 13

            assert observer.values == [8, 13, 15]

    def test_peek_cells_compare_equal_same_cell(self):
        """Test that peeks cells compare equal when their argument cells are equal."""

        a = mutable(0)

        p1 = a.peek
        p2 = a.peek

        assert p1 == p2
        assert hash(p1) == hash(p2)

    def test_peek_cells_compare_not_equal_different_cells(self):
        """Test that peek cells compare not equal when their argument cells are not equal."""

        a = mutable(0)
        b = mutable(0)

        p1 = a.peek
        p2 = b.peek

        assert p1 != p2
        assert p1 == p1

    def test_peek_cells_manage_same_observers(self):
        """Test that peeks cells manage the same set of observers for a given argument cell."""

        counter = LifecycleCounter()
        a = LifecycleTestCell(1, counter)

        def p():
            return a.peek

        assert counter.count_dispose == 0

        with observe(p()) as observer:
            p().remove_observer(observer)

            assert counter.count_init == 1
            assert counter.count_dispose == 1

    def test_remove_peek_observer(self):
        """Test that the correct observer is removed when removing a peek cell observer."""

        counter = LifecycleCounter()
        a = LifecycleTestCell(1, counter)

        def p():
            return a.peek

        assert counter.count_dispose == 0

        with observe(p()):
            observer = ValueTestObserver()
            p().remove_observer(observer)

            assert counter.count_init == 1
            assert counter.count_dispose == 0
