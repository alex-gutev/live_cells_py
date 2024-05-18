from .extension import cell_function, cell_extension
from .computed import computed, none
from .compute_cell import ComputeCell
from .keys import ValueKey

@cell_extension
def logand(a, b):
    """Create a cell that computes the logical **and** of this cell and ``b``.

    .. note::

       Cells returned by this method compare equal when called on the
       same object and the same arguments are provided.

    :param b: The operand cell.
    :type b: Cell

    :returns: A cell which evaluates to the logical **and** of this
              cell's value and the value of ``b``.

    :rtype: Cell

    """

    return ComputeCell(
        lambda: a.value and b.value,
        {a, b},
        key = AndCellKey(a, b)
    )

@cell_extension
def logor(a, b):
    """Create a cell that computes the logical **or** of this cell and ``b``.

    .. note::

       Cells returned by this method compare equal when called on the
       same object and the same arguments are provided.

    :param b: The operand cell.
    :type b: Cell

    :returns: A cell which evaluates to the logical **or** of this
              cell's value and the value of ``b``.

    :rtype: Cell

    """

    return ComputeCell(
        lambda: a.value or b.value,
        {a, b},
        key = OrCellKey(a, b)
    )

@cell_extension
@cell_function(key=lambda a: NotCellKey(a))
def lognot(a):
    """Create a cell that computes the logical not of this cell.

    .. note::

       Cells returned by this method compare equal when called on the
       same object.

    :returns: A cell which evaluates to the logical not of the value
              of this cell.

    :rtype: Cell

    """

    return not a

@cell_extension
def select(cond, if_true, if_false=None):
    """Create a new cell which selects between the values of two cells based on ``cond``.

    If the value of ``cond`` is *True*, the cell evaluates to the
    value of the ``if_true`` cell. If ``cond`` is *False*, the cell
    evaluates to the value of the ``if_false`` cell.

    If ``if_false`` is *None*, the previous value of the cell is
    preserved when ``cond`` is *False*.

    :param cond: A condition cell evaluating to a boolean.
    :type cond: Cell

    :param if_true: Cell to evaluate to when ``cond`` is *True*.
    :type if_true: Cell

    :param if_false: Cell to evaluate to when ``cond`` is *False*. If
                     *None* (the default), the value of the returned
                     cell is preserved when ``cond`` evaluates to
                     *False*.

    :type if_false: Cell

    :returns: A new cell.
    :type: Cell

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
