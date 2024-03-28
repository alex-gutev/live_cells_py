from .observer_state import ObserverCellState

class ComputeCellState(ObserverCellState):
    """Provides a cell state that computes a value as function of one or more argument cells.

    This class provides an implementation of a `CellState` for a cell
    that computes a value as a function of one or more argument
    cells. The class takes care of observing the argument cells,
    computing the value and caching it until the argument cells
    change.

    Subclasses must implement the `compute()` method, which should
    compute and return the value of the cell.

    """

    def __init__(self, cell, key, arguments):
        """Create a computed cell state with a given set of `arguments`."""

        super().__init__(
            cell = cell,
            key = key
        )

        self._arguments = arguments
        self._has_value = False

    @property
    def arguments(self):
        """The argument cells on which the value of this cell depends."""

        return self._arguments

    def compute(self):
        """Compute the cell's value.

        Subclasses must implement this method.

        """

        raise NotImplementedError

    @property
    def value(self):
        """Retrieve the value of the cell.

        If the cached value of the cell is stale, it is recomputed by
        calling `compute()`.

        """

        if self.stale:
            self._value = self.compute()

            self.stale = False
            self._has_value = True

        return self._value

    @value.setter
    def value(self, v):
        """Set the value of the cell.

        NOTE: This does not inform the observers of the cell, that its
        value has changed. This method should only be used to restore
        the value of a cell from persistent storage.

        """

        self._value = v

    def init(self):
        super().init()

        for arg in self._arguments:
            arg.add_observer(self)

    def dispose(self):
        for arg in self._arguments:
            arg.remove_observer(self)

        super().dispose()
