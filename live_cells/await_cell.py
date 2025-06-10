import asyncio

from .stateful_cell import StatefulCell
from .observer_state import ObserverCellState
from .exceptions import UninitializedCellError, PendingAsyncValueError
from .extension import cell_extension
from .async_state import AsyncCellState
from .computed import computed
from .maybe import Maybe
from .keys import ValueKey

class AwaitCell(StatefulCell):
    """A cell that *awaits* a coroutine held in the argument cell.

    The value of this cell is the completed value of the coroutine
    held in the argument cell. If the coroutine, raises an exception,
    then accessing this cell raises the same exception.

    .. important::

       If the value of this cell is accessed before the coroutine held
       in the argument cell has completed, a
       ``PendingAsyncValueError`` exception is raised.

    :param arg: The argument cell, which holds a coroutine
    :type arg: Cell

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

class AwaitCellKey(ValueKey):
    """Key identifying cells created with ``awaited``"""

@cell_extension
def awaited(self, *cells):
    """A cell that *awaits* the coroutine held in this cell.

    The value of the returned cell is the completed value of the
    coroutine held in this cell. If the coroutine, raises an
    exception, then accessing the value of the returned cell raises
    the same exception.

    .. important::

       If the value of the returned cell is accessed before the
       coroutine held in this cell has completed, a
       ``PendingAsyncValueError`` exception is raised.


    If multiple arguments are given a cell is returned that awaits the
    coroutine held in ``self`` and each cell in ``cells``. The value
    of the cell is a list holding the completed value of ``self``
    followed by the completed value of each cell in ``cells``. This is
    equivalent to the following.

    .. code-block:: python

       [await self(), await cells[0](), ...]

    The difference between a single call to ``awaited``:

    .. code-block:: python

       @computed
       def sum():
           x, y = awaited(a, b)()
           return x, y

    and multiple calls to ``awaited``:

    .. code-block:: python

       @computed
       def sum():
           return a.awaited()() + b.awaited()()

    becomes apparent when an updated to the argument cells is
    triggered by a common ancestor of both ``a`` and ``b``. With a
    single call to ``awaited``, the value of the ``sum`` cell is
    recomputed only once when both the coroutines held in ``a`` and
    ``b`` have completed. In the second example, the value of ``sum``
    is recomputed once when the coroutine held in ``a`` has completed
    and a second time when the coroutine held in ``b`` has completed.

    :param cells: Additional cells to ``await``
    :type cells: List[Cell]

    :returns: The await cell
    :rtype: Cell

    """

    if cells:
        @computed
        async def gathered():
            return await asyncio.gather(
                self(),
                *(c() for c in cells)
            )

        return AwaitCell(
            gathered,
            key=AwaitCellKey(self, *cells)
        )

    return AwaitCell(self, key=AwaitCellKey(self))
