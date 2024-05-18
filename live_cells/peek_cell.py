from .cell import Cell
from .extension import cell_extension

@cell_extension(name='peek')
@property
def peek(self):
    """Read the value of this cell without reacting to changes.

    This property returns a cell that has the same value as this cell
    but does not notify its observers when the value of this cell
    changes.

    This should be used rather than accessing the :any:`Cell.value`
    property directly to ensure that this cell is active.

    """

    return PeekCell(self)

class PeekCell(Cell):
    """A cell that has the same value as another cell but does not notify its observers."""

    def __init__(self, cell):
        """Create a PeekCell that evaluates to the value of `cell`."""

        super().__init__()

        self._cell = cell

    @property
    def value(self):
        return self._cell.value

    def add_observer(self, observer):
        self._cell.add_observer(PeekCellObserver(observer))

    def remove_observer(self, observer):
        self._cell.remove_observer(PeekCellObserver(observer))

    def __eq__(self, other):
        if isinstance(other, PeekCell):
            return self._cell == other._cell

        return NotImplemented

    def __hash__(self):
        return hash(self._cell)

class PeekCellObserver:
    """Wrapper that prevents cell observer methods from being called."""

    def __init__(self, observer):
        """Create a wrapper for an `observer`."""

        self._observer = observer

    def update(self, arg, did_change):
        pass

    def will_update(self, arg):
        pass

    def __eq__(self, other):
        if isinstance(other, PeekCellObserver):
            return self._observer == other._observer

        return NotImplemented

    def __hash__(self):
        return hash(self._observer)
