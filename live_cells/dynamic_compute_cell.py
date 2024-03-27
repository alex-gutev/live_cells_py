from .stateful_cell import StatefulCell
from .compute_state import ComputeCellState
from .cell import with_tracker, without_tracker

class DynamicComputeCell(StatefulCell):
    """A computed cell that determines its arguments at runtime."""

    def __init__(self, compute, key=None):
        """Create a computed cell with a given `compute` function.

        `compute` is a function of no arguments that is called to
        compute the value of the cell. The cells referenced within
        `compute`, using the function call syntax, are automatically
        registered as dependencies of the computed cell.

        The cell is identified by `key` if it is not None.

        """

        super().__init__(key=key)

        self._compute = compute

    @property
    @without_tracker
    def value(self):
        state = self.state

        if state is None:
            return self._compute()

        return state.value

    def create_state(self):
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

    @with_tracker(track_argument)
    def compute(self):
        return self.cell._compute()
