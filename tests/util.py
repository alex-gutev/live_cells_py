## Utilities used for testing

from contextlib import contextmanager

from live_cells.stateful_cell import StatefulCell, CellState

class CountTestObserver:
    """A cell observer that counts how many times its methods are called.

    `count_will_update` is the number of times `will_update` was
    called.

    `count_update` is the number of times `update` was called.

    """

    def __init__(self):
        self.count_will_update = 0
        self.count_update = 0

    def update(self, cell, did_change):
        self.count_update += 1

    def will_update(self, cell):
        self.count_will_update += 1

class ValueTestObserver:
    """A cell observer that records the values of the observed cell in a list.

    This observer records the value of the observed cell(s), in the
    list `values`, at every call to `update`.

    NOTE: Duplicate values are not recorded in `values`.

    """

    def __init__(self):
        self.values = []

        self._updating = False
        self._notify_count = 0
        self._did_change = False

    def will_update(self, cell):
        if not self._updating:
            assert self._notify_count == 0

            self._updating = True
            self._notify_count = 0
            self._did_change = False

        self._notify_count += 1

    def update(self, cell, did_change):
        if self._updating:
            assert self._notify_count > 0

            self._did_change = self._did_change or did_change

            self._notify_count -= 1

            if self._notify_count == 0:
                self._updating = False

                if self._did_change:
                    try:
                        value = cell.value

                        if not self.values or self.values[-1] != value:
                            self.values.append(value)

                    except:
                        pass

class LifecycleCounter:
    """Keeps track of how many times init() and dispose() were called.

    `count_init`: Number of times `init()` was called.
    `count_dispose`: Number of times `dispose() was called.

    """

    def __init__(self):
        self.count_init = 0
        self.count_dispose = 0

class LifecycleTestCell(StatefulCell):
    """A cell which counts how many times the state init() and dispose() methods were called."""

    def __init__(self, value, counter):
        """Create a lifecycle method counter cell.

        The cell's value is the constant `value`.

        When `init()` or `dipose()` are called, the `count_init` and
        `count_dispose` properties are incremented respectively.

        """

        super().__init__()

        self._value = value
        self._counter = counter

    @property
    def value(self):
        return self._value

    def create_state(self):
        return LifecycleTestState(
            cell = self,
            key = None,
            counter = self._counter
        )

class LifecycleTestState(CellState):
    """Maintains the state of a LifecycleTestCell."""

    def __init__(self, cell, key, counter):
        """Initialize with LifecycleCounter `counter`."""

        super().__init__(cell=cell, key=key)

        self.counter = counter

    def init(self):
        super().init()
        self.counter.count_init += 1

    def dispose(self):
        self.counter.count_dispose += 1
        super().dispose()


class MockException(Exception):
    """Used to test propagation of exceptions."""

    pass

@contextmanager
def observe(cell, observer=CountTestObserver()):
    """Add an `observer` to `cell` for the lifetime of a managed context.

    This is a context manager that adds the observer `observer` to
    `cell`, when entering the `with` block, and automatically removes
    it when exiting the context.

    ```
    observer = CountTestObserver()

    with observer(cell, CountTestObserver()):
       # observer is an observer of `cell` within the `with` block
       ...
    ```

    """

    cell.add_observer(observer)

    # Compute value to ensure cell is active
    try:
        cell.value

    except:
        pass

    try:
        yield observer

    finally:
        cell.remove_observer(observer)
