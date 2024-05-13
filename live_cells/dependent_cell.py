from .cell import Cell

class DependentCell(Cell):
    """A cell with a value that is dependent on a set of argument cells.

    This is not a complete Cell subclass, notably the definition of
    the `value` property is missing. The definition of the `value`
    property should be defined by subclasses.

    This cell should not hold any mutable state. Instead the `value`
    property should compute the cells value whenever it is accessed.

    """

    def __init__(self, arguments, key=None):
        """Create a cell dependent on the cells in `arguments`.

        The cell is identified by `key` if it is not None.

        """

        self._key = key
        self._arguments = arguments

    @property
    def key(self):
        """Key identifying the cell."""

        return self._key

    @property
    def arguments(self):
        """Set of cells on which the value of this cell depends."""

        return self._arguments

    def add_observer(self, observer):
        for arg in self.arguments:
            arg.add_observer(
                ObserverWrapper(observer)
            )

    def remove_observer(self, observer):
        for arg in self.arguments:
            arg.remove_observer(
                ObserverWrapper(observer)
            )

    def __eq__(self, other):
        if self is other:
            return True

        if isinstance(other, DependentCell):
            return self.key != None and other.key != None and self.key == other.key

        return NotImplemented

    def __hash__(self):
        return hash(self.key)

class ObserverWrapper:
    """Wrapper that replaces the cell instance passed to a cell observer."""

    def __init__(self, cell, observer):
        """Create a wrapper replacing the cell passed to observer with `cell`."""

        self.cell = cell
        self.observer = observer

    def update(self, arg, did_change):
        self.observer.update(self.cell, did_change)

    def will_update(self, arg):
        self.observer.will_update(self.cell)

    def __eq__(self, other):
        if isinstance(other, ObserverWrapper):
            return self.observer == other.observer and self.cell == other.cell

        return NotImplemented

    def __hash__(self):
        return hash(self.observer);
