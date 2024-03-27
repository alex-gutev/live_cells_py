from .stateful_cell import CellState

class ObserverCellState(CellState):
    """Provides a cell state that observes another cell.

    This class provides an implementation of a `CellState` and the
    cell observer interface. This allows subclasses to directly add
    this state as an observer to other cells.

    The implementation of the cell observer directly forwards the
    notifications to the observers of this cell. This behaviour can be
    changed by overriding `on_will_update` and `on_update`, which are
    called when `will_update` and `update` are called, respectively.

    This class also provides the following properties which can be
    accessed by subclasses:

    - stale

      If true the cell's value should be recomputed when it is
      accessed again. Note, when the cell's value is recomputed, stale
      should be reset to false.

    - updating

      Is a cell update cycle currently in progress?

    """

    def __init__(self, cell, key=None):
        super().__init__(
            cell = cell,
            key = key
        )

        self.stale = True
        self.updating = False

    def did_change(self):
        """Did the cell's value actually change during this update cycle?

        Currently not used.

        """

        return True

    def pre_update(self):
        """Called before the update cycle for this cell begins."""

        pass

    def post_update(self):
        """Called after the update cycle for this cell has ended."""

        pass

    def on_will_update(self):
        """Called after `will_update()` is called.

        The base implementation calls `will_update()` on the observers of
        this cell.

        NOTE: This method is only called once per update cycle.

        """

        self.notify_will_update()

    def on_update(self):
        """Called after `update()` is called.

        The base implementation calls `update()` on the observers of
        this cell.

        NOTE: This method is only called once per update cycle.

        """

        self.notify_update()

    # Cell Observer Methods

    def will_update(self, arg):
        if not self.updating:
            self.pre_update()

            self.updating = True

            self.on_will_update()
            self.stale = True

    def update(self, arg):
        if self.updating:
            self.on_update()

            self.updating = False
            self.post_update()
