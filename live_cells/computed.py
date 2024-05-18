from .dynamic_compute_cell import DynamicComputeCell
from .exceptions import StopComputeException

def computed(compute=None, key = None, changes_only = False):
    """Create a computed cell with dynamically determined arguments.

    A computed cell with compute function ``compute`` is
    created. ``compute`` is a function of no arguments, that is called
    to compute the value of the cell. The cells referenced within
    ``compute``, using the function call syntax, are automatically
    registered as dependencies of the cell such that when their values
    change the value of the computed cell is recomputed.

    .. note::

       This function may be used as a decorator by omitting the
       ``compute`` argument, in which case the decorated function is
       used as the compute function. The cell is then referenced using
       the name of the decorated function.

    :param compute: Function of no arguments called to compute the\
    value of the cell.

    :type compute: function

    :param key: Key identifying the cell if not *None*. Defaults to *None*.

    :param changes_only: If *True* the cell only notifies its\
    observers if its new value is not equal to its previous\
    value. Defaults to *False*.

    :returns: A computed cell.

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
