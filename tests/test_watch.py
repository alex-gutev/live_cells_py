from live_cells import watch, mutable, batch
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
