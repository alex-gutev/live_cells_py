from .dependent_cell import DependentCell

class ComputeCell(DependentCell):
    """A stateless computed cell with a user provided function.

    The value of this cell is computed whenever it is accessed.

    """

    def __init__(self, compute, arguments, key=None):
        """Create a computed cell a given `compute` function and `arguments`.

        When the value of this cell is accessed `compute` is called
        with no arguments. It should return the cell's value.

        The cell is identified by `key` if it is not None.

        """

        super().__init__(
            arguments = arguments,
            key = key
        )

        self.compute = compute

    @property
    def value(self):
        return self.compute()
