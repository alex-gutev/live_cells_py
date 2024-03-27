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
