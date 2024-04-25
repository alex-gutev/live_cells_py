from .dynamic_compute_cell import DynamicComputeCell
from .exceptions import StopComputeException

def computed(compute, key = None, changes_only = False):
    """Create a computed cell with dynamically determined arguments.

    A computed cell with compute function `compute` is
    created. `compute` is a function of no arguments, that is called
    to compute the value of the cell. The cells referenced within
    `compute`, using the function call syntax, are automatically
    registered as dependencies of the cell.

    The cell is identified by `key` if it is not None.

    If `changes_only` is True, the cell only notifies its observers if
    its value has actually changed.

    """

    return DynamicComputeCell(
        compute = compute,
        key = key,
        changes_only = changes_only
    )

def computed_cell(key = None, changes_only = False):
    """Define a computed cell with a value computed by the decorated function.

    When this is applied a decorator on a function, the definition is
    replaced with a dynamic computed cell which computes its value
    using the decorated function. The dependencies of the cell are
    automatically discovered, from the cells referenced in the
    function using the function call syntax.

    The cell is identified by `key` if it is not None.

    If `changes_only` is True, the cell only notifies its observers if
    its value has actually changed.

    """

    def decorator(fn):
        return computed(fn, key=key, changes_only=changes_only)

    return decorator

def none(default_value=None):
    """Stop the computation of the current cell's value.

    When this method is called inside the value computation function
    of a cell, the cell's value is not updated. Instead the cell's
    current value is preserved.

    If this function is called during the computation of the cell's
    initial value, the cell's initial value is set to `default_value`.

    """

    raise StopComputeException(default_value)
