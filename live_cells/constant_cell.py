from .cell import Cell

class ConstantCell(Cell):
    """A cell holding a constant value.

    NOTE: ConstantCell's holding the same values compare equal.

    """

    def __init__(self, value):
        """Create a constant cell holding `value`."""

        self._value = value

    @property
    def value(self):
        return self._value

    def add_observer(self, observer):
        pass

    def remove_observer(self, observer):
        pass

    def __eq__(self, other):
        if isinstance(other, ConstantCell):
            return self.value == other.value

        return NotImplemented

    def __hash__(self):
        return hash(self.value)

def value(value):
    """Create a cell with a constant ``value``.

    The value of a constant cell never changes and its observers are
    never notified.

    .. note::

       Two constant cells compare equal if their values are equal.

    :param value: The constant value of the cell.

    :returns: A constant cell.

    """

    return ConstantCell(value)
