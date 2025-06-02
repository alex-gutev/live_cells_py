import asyncio

from .stateful_cell import StatefulCell
from .compute_state import ComputeCellState
from .tracking import without_tracker, ArgumentTracker
from .exceptions import StopComputeException

from .changes_only_state import ChangesOnlyState

class DynamicComputeCell(StatefulCell):
    """A computed cell that determines its arguments at runtime."""

    def __init__(self, compute, key=None, changes_only=False):
        """Create a computed cell with a given `compute` function.

        `compute` is a function of no arguments that is called to
        compute the value of the cell. The cells referenced within
        `compute`, using the function call syntax, are automatically
        registered as dependencies of the computed cell.

        The cell is identified by `key` if it is not None.

        If `changes_only` is True, the cell only notifies its
        observers if its value has actually changed.

        """

        super().__init__(key=key)

        self._compute = compute
        self._changes_only = changes_only

    @property
    @without_tracker
    def value(self):
        state = self.state

        if state is None:
            try:
                return self._compute()

            except StopComputeException as e:
                return e.default_value

        return state.value

    def create_state(self):
        if asyncio.iscoroutinefunction(self._compute):
            if self._changes_only:
                return AsyncDynamicComputeChangesOnlyCellState(self, self.key)

            return AsyncDynamicComputeCellState(self, self.key)

        if self._changes_only:
            return DynamicComputeChangesOnlyCellState(self, self.key)

        return DynamicComputeCellState(self, self.key)

class DynamicComputeCellState(ComputeCellState):
    """Maintains the state of a DynamicComputeCell."""

    def __init__(self, cell, key):
        super().__init__(
            cell = cell,
            key = key,
            arguments = set()
        )

    def track_argument(self, arg):
        """Register `arg` as a dependency of this cell."""

        if arg not in self.arguments:
            arg.add_observer(self)
            self.arguments.add(arg)

    def compute(self):
        with ArgumentTracker(self.track_argument):
            return self.cell._compute()

class DynamicComputeChangesOnlyCellState(ChangesOnlyState, DynamicComputeCellState):
    """A DynamicComputeCellState that checks whether the cell value has changed.

    This state only notifies the observers of the cell, if the new
    value of the cell is not equal to the previous value.

    """

    pass


## Async Computed Cells

class AsyncDynamicComputeCellState(DynamicComputeCellState):
    """Variant of DynamicComputeCellState that supports async compute functions."""

    async def compute(self):
        with ArgumentTracker(self.track_argument):
            return await self.cell._compute()

class AsyncDynamicComputeChangesOnlyCellState(DynamicComputeChangesOnlyCellState):
    """Variant of DynamicComputeChangesOnlyCellState that supports async compute functions."""

    async def compute(self):
        with ArgumentTracker(self.track_argument):
            return await self.cell._compute()
