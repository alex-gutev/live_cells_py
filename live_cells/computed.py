from .dynamic_compute_cell import DynamicComputeCell

def computed(compute, key = None):
    """Create a computed cell with dynamically determined arguments.

    A computed cell with compute function `compute` is
    created. `compute` is a function of no arguments, that is called
    to compute the value of the cell. The cells referenced within
    `compute`, using the function call syntax, are automatically
    registered as dependencies of the cell.

    The cell is identified by `key` if it is not None.

    """
    return DynamicComputeCell(
        compute = compute,
        key = key
    )

def computed_cell(key = None):
    """Define a computed cell with a value computed by the decorated function.

    When this is applied a decorator on a function, the definition is
    replaced with a dynamic computed cell which computes its value
    using the decorated function. The dependencies of the cell are
    automatically discovered, from the cells referenced in the
    function using the function call syntax.

    The cell is identified by `key` if it is not None.

    """

    def decorator(fn):
        return computed(fn, key=key)

    return decorator
