from .extension import cell_function, cell_extension
from .computed import computed, none
from .compute_cell import ComputeCell
from .keys import ValueKey

@cell_extension
def logand(a, b):
    """Create a cell that computes the logical and of the values of cells `a` and `b`.

    A keyed cell is returned, which is unique for a given `a` and `b`.

    """

    return ComputeCell(
        lambda: a.value and b.value,
        {a, b},
        key = AndCellKey(a, b)
    )

@cell_extension
def logor(a, b):
    """Create a cell that computes the logical or of the values of cells `a` and `b`.

    A keyed cell is returned, which is unique for a given `a` and `b`.

    """

    return ComputeCell(
        lambda: a.value or b.value,
        {a, b},
        key = OrCellKey(a, b)
    )

@cell_extension
@cell_function(key=lambda a: NotCellKey(a))
def lognot(a):
    """Create a cell that computes the logical not of the value of `a`.

    A keyed cell is returned, which is unique for a given `a`.

    """

    return not a

@cell_extension
def select(cond, if_true, if_false=None):
    """Create a new cell which selects between the values of two cells based on `cond`.

    If `cond` is True, the cell evaluates to the value of the
    `if_true` cell. If `cond` is False, the cell evaluates to the
    value of the `if_false` cell.

    If `if_false` is None, the previous value of the cell is preserved
    if `cond` is False.

    """
    if if_false is None:
        return computed(lambda: if_true() if cond() else none())

    else:
        return computed(lambda: if_true() if cond() else if_false())

## Keys

class AndCellKey(ValueKey):
    """Key identifying a cell created with logand."""

    pass

class OrCellKey(ValueKey):
    """Key identifying a cell created with logor."""

    pass

class NotCellKey(ValueKey):
    """Key identifying a cell created with not."""

    pass
