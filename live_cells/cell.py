from .tracking import ArgumentTracker

class Cell:
    """Base cell class.

    All cells should inherited this class.

    """

    @property
    def value(self):
        """The value of the cell."""

        raise NotImplementedError

    def __call__(self):
        """Retrieve the value of the cell and track it as a dependency.

        This should be used, instead of the :any:`Cell.value`
        property, when the cell needs to be registered automatically
        as a dependency.

        :returns: The value of the cell.

        """

        return ArgumentTracker.track(self)

    def add_observer(self, observer):
        """Add an ``observer`` to the cell.

        ``observer`` is notified whenever the value of this cell
        changes.

        :param observer: The observer to add to the cell.

        """

        raise NotImplementedError

    def remove_observer(self, observer):
        """Remove an ``observer`` from the cell.

        After ``observer`` is removed, it is no longer notified when
        the value of the cell changes.

        .. note::

           To remove a given ``observer``, this method has to be
           called the same number of times as `add_observer` was
           called for the same `observer`.

        :param observer: The observer to remove.

        """

        raise NotImplementedError
