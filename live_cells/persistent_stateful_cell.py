from .stateful_cell import StatefulCell

class InactivePersistentStatefulCellError(Exception):
    """Raised when attempting to access the state of a PersistentStatefulCell while it is inactive."""

    pass

class PersistentStatefulCell(StatefulCell):
    """A StatefulCell with a state that is created before the cell is observed.

    This cell guarantees that a non-disposed state is returned
    whenever `state` is accessed, even if the cell does not have any
    observers, as long as `key` is null.

    If `key` is non-null an `InactivePersistentStatefulCellError`
    exception is thrown if `state` is accessed when the cell is
    inactive.

    """

    @property
    def state(self):
        if self.key is None:
            return self._ensure_state()

        state = super().state

        if state is None:
            raise InactivePersistentStatefulCellError

        return state
