from contextlib import contextmanager

from .stateful_cell import CellState
from .persistent_stateful_cell import PersistentStatefulCell

class MutableCell(PersistentStatefulCell):
    """A cell which can have its value property set directly.

    When the value property is set, the observers of the cell are
    notified of the change.

    """

    def __init__(self, value = None, key = None):
        """Create a mutable cell initialized to `value`.

        The cell is identified by `key` if it is not None.

        """

        super().__init__(key=key)

        self._value = value
        self._mutable_state = None

    @property
    def value(self):
        return self.state.value

    @value.setter
    def value(self, value):
        """Set the value of the cell and notify its observers."""

        self.state.value = value

    def create_state(self):
        if self._mutable_state is None or self._mutable_state.disposed:
            self._mutable_state = self.create_mutable_state(
                self._mutable_state if self.key is None else None
            )

        return self._mutable_state

    def create_mutable_state(self, old_state):
        """Create a new mutable cell state.

        `old_state` is the previous cell state or None if no state has
        been created for this cell.

        """

        return MutableCellState(
            cell = self,
            key = self.key,
            value = old_state.value if old_state is not None else self._value
        )

class MutableCellState(CellState):
    """Maintains the state of a mutable cell."""

    ## Batch Update State

    _is_batch = False
    _batched = set()

    def __init__(self, cell, key, value):
        """Create a mutable cell state with an initial `value`."""

        super().__init__(
            cell = cell,
            key = key
        )

        self._value = value

    @property
    def value(self):
        """Retrieve the cell's value."""

        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the cell and notify the observers."""

        if self.disposed:
            self._value = value
            return

        if self.value != value:
            self.notify_will_update()
            self._value = value

            if self.is_batch:
                self.add_to_batch()

            else:
                self.notify_update()

    @property
    def is_batch(self):
        """Is a batch update currently in effect?"""

        return self._is_batch

    def add_to_batch(self):
        """Adds this state to the current batch's list of modified cell states."""

        self._batched.add(self)

    @classmethod
    def _begin_batch(cls):
        """Begin a batch update."""

        cls._is_batch = True
        cls._batched.clear()

    @classmethod
    def _end_batch(cls):
        """End the current batch update and update all the affected cells.

        This calls `notify_update()` on all cell states that were
        added to the current batch with `add_to_batch()`.

        """

        assert cls._is_batch

        cls._is_batch = False

        for state in cls._batched:
            state.notify_update()

        cls._batched.clear()

def mutable(value = None, key = None):
    """Create a mutable cell with an initial ``value``.

    The value of a mutable cell can be changed by setting its
    ``value`` property.

    :param value: The initial value of the cell, defaults to *None*.

    :param key: Key identifying the cell if not *None*, defaults to *None*.

    :returns: A mutable cell.

    """

    return MutableCell(value=value, key = key)


@contextmanager
def batch():
    """Batch changes to mutable cells within a given managed context.

    When this context manager is used, the observers of the mutable
    cells that are set within the *with* block managed by the context
    manager, are only notified when exiting the context.

    This has no effect when used when a batching is already in effect
    before the context manager is created.

    .. code-block::
       :caption: Example

       with batch():
           a.value = 1
           b.value = 2

       # Observers of `a` and `b` are only notified when
       # exiting the `with` block.

    """

    batching = not MutableCellState._is_batch

    if batching:
        MutableCellState._begin_batch()

    try:
        yield

    finally:
        if batching:
            MutableCellState._end_batch()

def batched(fn):
    """Apply the :any:`batch` context manager to the decorated function.

    This decorator is equivalent to replacing wrapping a call to
    ``fn`` with the following:

    .. code-block::

       with batch():
           fn()

    :param fn: A function
    :type fn: function

    :returns: A function that calls ``fn`` while applying cell batching.
    :rtype: function

    """

    def wrapper(*args, **kwargs):
        with batch():
            fn(*args, **kwargs)

    return wrapper
