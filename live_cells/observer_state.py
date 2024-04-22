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

        self._changed_dependencies = 0
        self._did_change = False

    def did_change(self):
        """Did the cell's value actually change during this update cycle?"""

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

    def on_update(self, did_change):
        """Called after `update()` is called.

        The base implementation calls `update()` on the observers of
        this cell.

        NOTE: This method is only called once per update cycle.

        """

        self.notify_update(did_change=did_change)

    # Cell Observer Methods

    def will_update(self, arg):
        if not self.updating:
            assert self._changed_dependencies == 0

            self.pre_update()

            self.updating = True
            self._did_change = False
            self._changed_dependencies = 0

            self.on_will_update()
            self.stale = True

        self._changed_dependencies += 1

    def update(self, arg, did_change):
        if self.updating:
            assert self._changed_dependencies > 0

            self._changed_dependencies -= 1
            self._did_change = self._did_change or did_change

            if self._changed_dependencies == 0:
                self.stale = self.stale or self._did_change
                self.on_update(self._did_change and self.did_change())

                self.updating = False

                if self._did_change:
                    self.post_update()
