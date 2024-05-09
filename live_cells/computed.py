from .dynamic_compute_cell import DynamicComputeCell
from .exceptions import StopComputeException

def computed(compute=None, key = None, changes_only = False):
    """Create a computed cell with dynamically determined arguments.

    A computed cell with compute function `compute` is
    created. `compute` is a function of no arguments, that is called
    to compute the value of the cell. The cells referenced within
    `compute`, using the function call syntax, are automatically
    registered as dependencies of the cell.

    The cell is identified by `key` if it is not None.

    If `changes_only` is True, the cell only notifies its observers if
    its value has actually changed.

    This function may be used as a decorator by omitting the `compute`
    argument, in which case the decorated function is used as the
    compute function. The cell can then be referenced using the name
    of the decorated function.

    """

    if compute is None:
        def decorator(fn):
            return computed(fn, key, changes_only)

        return decorator

    return DynamicComputeCell(
        compute = compute,
        key = key,
        changes_only = changes_only
    )

def none(default_value=None):
    """Stop the computation of the current cell's value.

    When this method is called inside the value computation function
    of a cell, the cell's value is not updated. Instead the cell's
    current value is preserved.

    If this function is called during the computation of the cell's
    initial value, the cell's initial value is set to `default_value`.

    """

    raise StopComputeException(default_value)
