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
    """Create a *wait cell* that *awaits* one or more *asynchronous cells*.

    The value of the returned cell is the completed value of the
    *awaitable* held in ``self``. If the *awaitable*, or the cell
    ``self`` itself, raises an exception then accessing the value of
    the returned cell raises the same exception.

    .. important::

       If the value of the returned cell is accessed before the
       coroutine held in ``self`` has completed, a
       :any:`PendingAsyncValueError` exception is raised.


    If multiple arguments are given, a cell is returned that *awaits* the
    *awaitables* held in ``self`` and each cell in ``cells``. The value
    of the cell is a list holding the completed value of ``self``
    followed by the completed value of each cell in ``cells``. This is
    equivalent to the following:

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

    becomes apparent when an update to the *asynchronous cells* is
    triggered by a common ancestor of the cells. With a single call to
    ``waited``, the value of the ``sum`` cell is recomputed only once
    when both the *awaitables* held in ``a`` and ``b`` have
    completed. In the second example, the value of ``sum`` is
    recomputed once when the *awaitable* held in ``a`` has completed
    and a second time when the *awaitable* held in ``b`` has
    completed.

    This function also accepts a number of keyword arguments that
    modify the behaviour of the cell.

    The ``reset`` keyword argument controls whether the value of the
    cell is reset when the values of the asynchronous cells
    changes.

    By default this is ``True``, which means that when the values of
    the asynchronous cells changes the value of the returned *wait
    cell* is reset. Accessing the value of the returned cell at this
    point results in a :any:`PendingAsyncValueError` exception being
    raised, until the *awaitables* held in the asynchronous cells have
    completed.

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


    The ``queue`` keyword argument controls what happens when the
    values of the asynchronous cells change before the *awaitables*,
    for which the *wait cell* is currently waiting, have completed.

    If ``queue`` is True, when the values of the asynchronous cells
    change, the *wait cell* first waits for the previous *awaitables*
    to complete, and only then waits for the new *awaitables*. The
    value of the *wait cell* is updated in the order in which the
    *awaitables* were assigned to the asynchronous cell and not
    necessarily in the order of completion.

    If ``queue`` is False, the default, the *wait cell* only waits for
    the last *awaitable* and ignores previous *awaitables* that have
    not completed.

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

    .. attention::

       The ``queue`` argument has no effect if ``reset`` is
       True.

    :param cells: Additional cells to ``await``
    :type cells: List[Cell]

    The following keyword arguments are accepted:

    :param reset: If True (the default), the value of the cell is
                  reset, whenever the values of the asynchronous cells
                  change. Otherwise the last completed value (or
                  exception) is retained until the new *awaitables* have
                  completed.

    :type reset: bool

    :param queue: If true, the returned cell waits for all
                  `awaitables` that were assigned to the asynchronous
                  cell(s) to complete. If false, the cell only waits
                  for the last *awaitables* that were assigned.

    :type queue: bool

    :returns: The *wait cell*
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
    """Create a *wait cell*, as if by :any:`waited` and access its value.

    Calling this function is equivalent to:

    .. code-block:: python

       waited(self, *cells, **kwargs)()

    This function accepts the same positional and keyword arguments as
    :any:`waited`.

    :returns: The value of the *wait cell*

    """

    return waited(self, *cells, **kwargs)()
