from live_cells import watch, mutable, batch, computed
from .util import LifecycleCounter, LifecycleTestCell

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
