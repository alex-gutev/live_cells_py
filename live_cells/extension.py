import functools

from .cell import Cell
from .compute_cell import ComputeCell

def cell_function(compute=None, key=None):
    """Create a function that is applied on cells and returns a new cell.

    This transform the function `compute` into a function that accepts
    cells as arguments and returns a new ComputeCell which evaluates
    to `compute` applied on the values of the argument cells.

    If `key` is not None, it is called with the arguments provided to
    the `compute` function to create the key for the cell.

    Can be used a decorator.

    """

    if compute is None:
        def decorator(fn):
            return cell_function(fn, key)

        return decorator

    @functools.wraps(compute)
    def wrapper(*args):
        return ComputeCell(
            lambda: compute(*(arg.value for arg in args)), set(args),
            key = key(*args) if key is not None else None
        )

    return wrapper

def cell_extension(fn = None, name=None):
    """Add `fn` as a method to all cell objects.

    `fn` is added as a method to the Cell class under the given `name`
    or the name of `fn` if `name` is None.

    This function may be used as a decorator.

    """

    if fn is None:
        def decorator(fn):
            return cell_extension(fn, name)

        return decorator

    setattr(Cell, name if name is not None else fn.__name__, fn)

    return fn
