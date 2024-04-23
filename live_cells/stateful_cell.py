from .cell import Cell

class StatefulCell(Cell):
    """Base class for a cell that maintains a state.

    The state of the cell should be stored in a separate `CellState`
    object, which is created after the cell's first observer is added
    and destroyed after its last observer is removed.

    Multiple `StatefulCell`s with the same not None key, share the
    same `CellState` object.

    """

    def __init__(self, key=None):
        """Create a StatefulCell identified by `key`.

        If `key` is None, it does not share its state with any other
        cell.

        """

        self.key = key
        self._state = None

    @property
    def state(self):
        """Retrieve the cell state if it has been created.

        If the state has not been created, or it has been destroyed,
        None is returned.

        """

        return self._get_state()

    def create_state(self):
        """Create the cell's state."""

        raise NotImplementedError

    def add_observer(self, observer):
        self._ensure_state().add_observer(observer)

    def remove_observer(self, observer):
        state = self._get_state()

        if state is not None:
            state.remove_observer(observer)

    def __eq__(self, other):
        if isinstance(other, StatefulCell) and self.key is not None and other.key is not None:
            return self.key == other.key

        return NotImplemented

    def __hash__(self):
        return hash(self.key)

    # Private

    def _ensure_state(self):
        """Retrieve the cell's state, creating it if necessary."""

        if self._state is None or self._state.disposed:
            self._state = GlobalStateMap.instance.get(self.key, self.create_state)

        return self._state

    def _get_state(self):
        """Retrieve the cell's state if it has been created."""

        if self._state is None or self._state.disposed:
            self._state = GlobalStateMap.instance.maybe_get(self.key)

        return self._state


class CellState:
    """Maintains the state of a stateful cell.

    This class is intended to serve as the base class for cell state
    classes. It provides functionality for adding, removing and
    notifying the cell's observers.

    """
    def __init__(self, cell, key=None):
        """Create a cell state object.

        The state object is created for a `cell` identified by
        `key`.

        If `key` is None then `cell` is the only cell using this state
        object.

        """

        self.cell = cell
        self.key = key

        self._observers = {}
        self._disposed = False

        self._notify_count = 0

    @property
    def disposed(self):
        """Has this state been disposed?

        Once a state has been disposed it should no longer be used.

        """

        return self._disposed

    def init(self):
        """Called before the first observer is added.

        This should be overridden by subclasses to include any setup
        logic required for the cell's functionality.

        """

        pass

    def dispose(self):
        """Called after the last observer is removed.

        This should be overridden by subclasses to include the cleanup
        logic for the cell.

        """

        self._disposed = True
        GlobalStateMap.instance.remove(self.key)

    def add_observer(self, observer):
        """Add an observer."""

        assert not self._disposed, 'CellState used after disposal.'

        if not self._observers:
            self.init()

        self._observers[observer] = self._observers.get(observer, 0) + 1

    def remove_observer(self, observer):
        """Remove an observer."""

        assert not self._disposed, 'CellState used after disposal.'

        if observer in self._observers:
            count = self._observers[observer]

            if count > 1:
                self._observers[observer] -= 1

            else:
                del self._observers[observer]

                if not self._observers:
                    self.dispose()

    def notify_will_update(self):
        """Notify the observers that the cell's value will change.

        This method calls `will_update` on each observer.

        """

        assert not self._disposed, 'CellState used after disposal.'

        self._notify_count += 1
        assert self._notify_count > 0, r'''Notify count is less than or equal to zero at the start of the update cycle.

        This indicates a bug in live_cells unless the error originates
        from a cell class provided by third-party code.'''

        # TODO: Make copy of observers
        for observer in self._observers:
            try:
                observer.will_update(self.cell)

            except: # TODO: Print log
                pass

    def notify_update(self, *, did_change=True):
        """Notify the observers that the cell's value has changed.

        This method calls `update` on each observer.

        A value of False for `did_change` indicates that the cell's
        value has not changed. A value of True indicates that it may
        have changed.

        """

        assert not self._disposed, r'''Notify count is less than zero when calling CellState.notify_update().

        This indicates a bug in live_cells unless the error originates
        from a cell class provided by third-party code.'''


        self._notify_count -= 1
        assert self._notify_count >= 0

        # TODO: Make copy of observers
        for observer in self._observers:
            try:
                observer.update(self.cell, did_change)

            except: # TODO: Print log
                pass

class GlobalStateMap:
    """Mas cell keys to shared cell states."""

    _instance = None

    @classmethod
    @property
    def instance(cls):
        """Retrieve the singleton instance."""

        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self):
        self.states = {}

    def get(self, key, create):
        """Retrieve the state for the cell identified by `key`, creating it if it exists.

        If the state for the cell identified by `key` has not been
        created, `create()` is called to create it and the resulting
        state is stored in the map.

        """

        if key is None:
            return create()

        if key not in self.states:
            self.states[key] = create()

        return self.states[key]

    def maybe_get(self, key):
        """Retrieve the state for the cell identified by `key`.

        If the state for the cell identified by `key` has not been
        created, None is returned.

        """

        return self.states.get(key)

    def remove(self, key):
        """Remove the state for the cell identified by `key` from the map."""

        if key in self.states:
            del self.states[key]
