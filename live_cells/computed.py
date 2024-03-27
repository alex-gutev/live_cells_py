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
