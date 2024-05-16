from .extension import cell_function, cell_extension
from .computed import computed, none
from .keys import ValueKey

@cell_extension
def on_error(self, other, type=None):
    """Create a cell that evaluates to another cell when `self` raises an exception.

    When an exception is raised by `self`, the returned cell evaluates
    to the value of `other.

    If `type` is not None, the returned cell evaluates to the value of
    `other` only when an exception of the same type as that provided
    in `type` is raised.

    A keyed cell is returned that is unique for a given `self`,
    `other` and `type`.

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
    """Create a cell that captures exceptions raised by `self`.

    The returned cell evaluates to the last exception raised by
    `self`.

    If `all` is True, the returned cell evaluates to None when `self`
    does not raise an exception. NOTE: The value of the returned cell
    is None until the first exception raised by `self`, regardless of
    the value of `all`.

    If `type` is not None, the returned cell only captures exceptions
    which are of the type provided in `type`.

    A keyed cell is returned that is unique for a given `self`, `all`
    and `type`.

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
