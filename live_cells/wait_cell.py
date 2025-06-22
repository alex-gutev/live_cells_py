import asyncio

from .stateful_cell import StatefulCell
from .observer_state import ObserverCellState
from .exceptions import UninitializedCellError, PendingAsyncValueError
from .extension import cell_extension
from .async_state import AsyncCellState
from .computed import computed
from .maybe import Maybe
from .keys import ValueKey

class WaitCell(StatefulCell):
    """A cell that *awaits* an *awaitable* held in the argument cell.

    The value of this cell is the completed value of the *awaitable*
    held in the argument cell. If the *awaitable*, raises an
    exception, then accessing this cell raises the same exception.

    .. important::

       If the value of this cell is accessed before the *awaitable*
       held in the argument cell has completed, a
       :any:`PendingAsyncValueError` exception is raised.

    .. note::

       The difference between this cell and ``AwaitCell`` is that the
       value of this cell is not reset when the value of the argument
       cell changes. Instead, the completed value of the last
       *awaitable* is kept until the new *awaitable* completes.

    :param arg: The argument cell, which holds an *awaitable*
    :type arg: Cell

    :param last_only: If True, only the last *awaitable* assigned to
                      the argument cell is awaited. If False, the cell
                      waits for every *awaitable* assigned to the
                      argument cell to complete.

    :type last_only: bool

    :param key: Key identifying the cell

    """

    def __init__(self, arg, last_only=False, key=None):
        super().__init__(key=key)

        self.arg = arg
        self.last_only = last_only

    @property
    def value(self):
        state = self.state

        if state is not None:
            return state.value

        raise UninitializedCellError

    def create_state(self):
        return WaitCellState(
            self,
            key=self.key
        )

class WaitCellState(AsyncCellState, ObserverCellState):
    """The state for a ``WaitCell``"""

    def __init__(self, cell, key):
        super().__init__(
            cell=cell,
            key=key
        )

        self.arg = cell.arg
        self.last_only = cell.last_only

    def on_will_update(self):
        # Prevent observers from being notified before awaitable
        # completion

        pass

    def on_update(self, did_change):
        # Prevent observers from being notified before awaitable
        # completion

        pass
