import pytest

class EmptyObserver:
    """An observer which does nothing."""

    def will_update(self, cell):
        pass

    def update(self, cell):
        pass

class ObserverUtil:
    """Utilities for adding observers to cells.

    This class provides functionality for adding observers to cells,
    using the `add` and `observe` methods.

    When used in a test fixture, all observers added through this
    class are removed after the test has finished.

    """

    def __init__(self):
        self.observers = []

    def add(self, cell, observer):
        """Add an `observer` to `cell`."""

        cell.add_observer(observer)
        self.observers.append((cell, observer))

        try:
            # Reference the value to ensure the cell is fully initialized
            cell.value

        except:
            pass

    def observe(self, cell):
        """Add an observer to cell.

        Use this method when you don't care what observer is added to
        `cell` but want to ensure that `cell` is observed.

        """

        self.add(cell, EmptyObserver)

    def remove_all(self):
        """Remove all observers added with `add` and `observe`."""

        for (cell, observer) in self.observers:
            cell.remove_observer(observer)

        self.observers = []


@pytest.fixture()
def observers():
    """Provides functionality for adding observers to cells.

    The observers added via this fixture's `add` and `observe` method,
    are automatically removed after the test runs.

    """

    util = ObserverUtil()
    yield util

    util.remove_all()
