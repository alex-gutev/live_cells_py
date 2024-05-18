from .extension import cell_function, cell_extension
from .computed import computed, none
from .keys import ValueKey

@cell_extension
def on_error(self, other, type=None):
    """Create a cell that evaluates to another cell when this cell raises an exception.

    When an exception is raised while computing the value of this
    cell, the returned cell evaluates to the value of ``other``.

    If ``type`` is not *None*, the returned cell evaluates to the value of
    ``other`` only when an exception of the same type as that provided
    in ``type`` is raised.

    .. note::

       Cells returned by this method compare equal if the same
       ``other`` and ``type`` are provided for both cells.

    :param other: The cell to evaluate to when this cell raises an exception.
    :type other: Cell

    :param type: Type of exceptions to handle or *None* (default) to
                 handle all exceptions.

    :returns: A new cell.
    :rtype: Cell

    """

    @computed(key = OnErrorCellKey(self, other, type))
    def cell():
        try:
            return self()

        except Exception as e:
            if type is None or isinstance(e, type):
                return other()

            raise

    return cell

@cell_extension
def error(self, all=False, type=None):
    """Create a cell that captures exceptions raised by this cell.

    The returned cell evaluates to the last exception raised while
    computing the value of this cell..

    If ``type`` is not None, the returned cell only captures
    exceptions which are of the type provided in ``type``.

    .. note::

       Cells returned by this method compare equal if the same ``all``
       and ``type`` are provided for both cells.

    :param all: If *True*, the returned cell evaluates to *None* when
                this cell does not raise an exception. Defaults to
                *False*.

    :param type: The type of exceptions to capture or *None* (default)
                 to capture all exceptions.

    :returns: A new cell.
    :rtype: Cell

    .. note::

       The value of the returned cell is *None* until an exception is
       raised while computing the value of this cell, regardless of
       the value of ``all``.

    """

    @computed(key = ErrorCellKey(self, all, type), changes_only=True)
    def cell():
        try:
            self()

        except Exception as e:
            if type is None or isinstance(e, type):
                return e

        if not all:
            none()

        return None

    return cell


## Keys

class OnErrorCellKey(ValueKey):
    """Key identifying a cell created with on_error."""

class ErrorCellKey(ValueKey):
    """Key identifying a cell created with error."""
