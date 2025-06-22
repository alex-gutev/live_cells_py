from .stateful_cell import StatefulCell
from .observer_state import ObserverCellState
from .exceptions import UninitializedCellError, PendingAsyncValueError
from .async_state import AsyncCellState
from .maybe import Maybe

class AwaitCell(StatefulCell):
    """A cell that *awaits* an *awaitable* held in the argument cell.

    The value of this cell is the completed value of the *awaitable*
    held in the argument cell. If the *awaitable*, raises an exception,
    then accessing this cell raises the same exception.

    .. important::

       If the value of this cell is accessed before the *awaitable*
       held in the cell has completed, a :any:`PendingAsyncValueError`
       exception is raised.

    :param arg: The argument cell, which holds an *awaitable*
    :type arg: Cell

    :param key: Key identifying the cell

    """

    def __init__(self, arg, key=None):
        super().__init__(key=key)

        self.arg = arg

    @property
    def value(self):
        state = self.state

        if state is not None:
            return state.value

        raise UninitializedCellError


    def create_state(self):
        return AwaitCellState(self, key=self.key)

class AwaitCellState(AsyncCellState, ObserverCellState):
    """Implements the cell state for an ``AwaitCell``"""

    def __init__(self, cell, key):
        super().__init__(
            cell = cell,
            key = key
        )

        self.arg = cell.arg
        self.last_only = True

    def on_update(self, did_change):
        if did_change:
            self._awaited_value = Maybe(
                error=PendingAsyncValueError()
            )

        super().on_update(did_change)
