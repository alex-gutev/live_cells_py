import asyncio

from .keys import ValueKey
from .computed import computed
from .extension import cell_extension
from .await_cell import AwaitCell
from .wait_cell import WaitCell

class WaitedCellKey(ValueKey):
    """Key identifying cells created with ``waited()``."""

@cell_extension
def waited(self, *cells, **kwargs):
    """Create an *await cell* that *awaits* the coroutine held in this cell.

    The value of the returned cell is the completed value of the
    coroutine held in this cell. If the coroutine, raises an
    exception, then accessing the value of the returned cell raises
    the same exception.

    .. important::

       If the value of the returned cell is accessed before the
       coroutine held in this cell has completed, a
       ``PendingAsyncValueError`` exception is raised.


    If multiple arguments are given, a cell is returned that awaits the
    coroutine held in ``self`` and each cell in ``cells``. The value
    of the cell is a list holding the completed value of ``self``
    followed by the completed value of each cell in ``cells``. This is
    equivalent to the following.

    .. code-block:: python

       [await self(), await cells[0](), ...]

    The difference between a single call to ``waited``:

    .. code-block:: python

       @computed
       def sum():
           x, y = waited(a, b)()
           return x, y

    and multiple calls to ``waited``:

    .. code-block:: python

       @computed
       def sum():
           return a.waited()() + b.waited()()

    becomes apparent when an update to the argument cells is
    triggered by a common ancestor of both ``a`` and ``b``. With a
    single call to ``waited``, the value of the ``sum`` cell is
    recomputed only once when both the coroutines held in ``a`` and
    ``b`` have completed. In the second example, the value of ``sum``
    is recomputed once when the coroutine held in ``a`` has completed
    and a second time when the coroutine held in ``b`` has completed.

    This function also accepts a number of keyword arguments that
    modify the behaviour of the cell.

    The ``reset`` keyword argument controls whether the value of the
    cell is reset when a new coroutine is assigned to the argument
    cell(s).

    By default this is ``True``, which means that assigning a new
    coroutine to the argument cell, resets the value of the returned
    await cell. Accessing the value of the returned cell at this point
    results in a ``PendingAsyncValueError`` exception being raised,
    until the coroutine has completed with a value or an error.

    .. code-block:: python

       async def coro1():
           await asyncio.sleep(1)
           return 1

       async def coro2():
           await asyncio.sleep(1)
           return 2

       arg = mutable(coro1)

       w1 = arg.waited()
       w2 = arg.waited(reset=False)

       await asyncio.sleep(2)

       # The values of both `w1` and `w2` are 1

       arg.value = coro2

       # Accessing the value of `w1` raises `PendingAsyncValueError`
       # The value of `w2` is still 1


    The ``queue`` keyword argument controls what happens when a new
    coroutine is assigned to the argument cell(s), before the previous
    coroutine has completed.

    If ``queue`` is True, when a new coroutine is assigned to the
    argument cell, the await cell first waits for the previous
    coroutine to complete, and only then waits for the new
    coroutine. The value of the await cell is updated in the order in
    which the coroutines are assigned to the argument cell and not
    necessarily in the order of completion.

    If ``queue`` is False, the await cell only waits for the last
    coroutine that was assigned to the argument cell.

    The following example illustrates the difference:

    .. code-block:: python

       async def coro1():
           await asyncio.sleep(5)
           return 1

       async def coro2():
           await asyncio.sleep(1)
           return 2

       arg = mutable(coro1)

       w1 = arg.waited(reset=False, queue=True)
       w2 = arg.waited(reset=False)

       @watch
       def watch_w1():
           print(f'W1 = {w1()}')

       @watch
       def watch_w2():
           print(f'W2 = {w2()}')

       # NOTE: There is no await meaning coro1 has not completed
       arg.value = coro2


    For ``w1`` two lines are printed: ``W1 = 1`` and ``W1 = 2``, while
    for ``w2`` only a single line ``W2 = 2`` is printed.

    .. note::

       The ``queue`` argument has no effect if ``reset`` is
       True.

    :param cells: Additional cells to ``await``
    :type cells: List[Cell]

    The following keyword arguments are accepted:

    :param reset: If True (the default), the value of the cell is
                  reset, whenever a new coroutine is assigned to an
                  argument cell. Otherwise the last completed value
                  (or exception) is retained until the new coroutine
                  has completed.

    :type reset: bool

    :param queue: If true, the returned cell waits for every
                  coroutine, that is assigned to the argument cell(s),
                  to complete. If false, the cell only waits for the
                  last coroutine that was assigned to the argument
                  cell(s).

    :returns: The await cell
    :rtype: Cell

    """

    reset = kwargs.get('reset', True)
    queue = kwargs.get('queue', False)

    arg = self

    if cells:
        @computed
        def gathered():
            async def gather(coros):
                return await asyncio.gather(*coros)

            return gather([
                self(),
                *(c() for c in cells)
            ])

        arg = gathered

    key = WaitedCellKey(reset, queue, self, *cells)

    if reset:
        return AwaitCell(arg, key=key)

    else:
        return WaitCell(
            arg,
            last_only=not queue,
            key=key
        )

@cell_extension
def wait(self, *cells, **kwargs):
    """Creates an *await cell*, as if by ``waited`` and accesses its value.

    Calling this function is equivalent to:

    .. code-block:: python

       waited(self, *cells, **kwargs)()

    This function accepts the same positional and keyword arguments as
    ``waited``.

    :returns: The value of the ``waited`` cell.

    """

    return waited(self, *cells, **kwargs)()
