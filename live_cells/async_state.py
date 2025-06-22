import asyncio
from asyncio import Future

from .observer_state import ObserverCellState
from .exceptions import PendingAsyncValueError
from .maybe import Maybe

class AsyncCellState:
    """Augments ``CellState`` with functionality for waiting for *awaitables*.

    This mixin provides functionality for creating a ``CellState``
    that updates its value when the *awaitable* held in the argument
    cell completes.

    The behaviour of this class is influenced by the value of the
    ``last_only`` property.

    If ``last_only`` is false, the state waits for the completion of
    every *awaitable* that is held in the argument cell. The values
    assigned to the cell associated with this state, are the completed
    values of the *awaitables* held in the argument cell. The
    assignments happen in the order, in which the *awaitables* are
    assigned to the argument cell and not necessarily in the order of
    completion of the *awaitables*.

    If ``last_only`` is true and the argument cell is assigned a new
    *awaitable* before the previous *awaitable* completes, the state only
    waits for the new *awaitable* to complete, and does not emit an
    update for the previous *awaitable*.

    """

    def init(self):
        super().init()

        self._task = None
        self._awaited_value = Maybe(error=PendingAsyncValueError())

        self.arg.add_observer(self)
        self._update_value(self._get_value())

    def dispose(self):
        self.arg.remove_observer(self)

        if self._task is not None:
            self._task.cancel()

        super().dispose()

    @property
    def value(self):
        return self._awaited_value.unwrap()

    def post_update(self):
        super().post_update()

        if self.last_only and self._task is not None:
            self._task.cancel()
            self._task = None

        self._update_value(self._get_value())

    def _get_value(self):
        return Maybe.wrap_async(lambda: self.arg.value)

    def _update_value(self, future_value):
        self._task = asyncio.create_task(
            self.wait_future(self._task, future_value)
        )

    async def wait_future(self, task, future_value):
        if task is not None:
            await asyncio.shield(task)

        self._set_value(await future_value)

    def _set_value(self, value):
        self.notify_will_update()

        self.stale = False
        self._awaited_value = value

        self.notify_update()
