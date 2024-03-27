class Cell:
    """Base cell class.

    All cells should inherited this class.

    """

    @property
    def value(self):
        """Retrieve the value of the cell."""

        raise NotImplementedError()

    def __call__(self):
        """Retrieve the value of the cell and track it as a dependency.

        This should be used, instead of the `value` property, when the
        cell needs to be registered automatically as a dependency.

        """

        track_argument(self)
        return self.value

    def add_observer(self, observer):
        """Add an `observer` to the cell.

        `observer` is notified whenever the value of this cell
        changes.

        """

        raise NotImplementedError()

    def remove_observer(self, observer):
        """Remove an `observer` from the cell.

        After `observer` is removed, it is no longer notified when the
        value of the cell changes.

        This method has to be called the same number of times as
        `add_observer` was called for the same `observer`, in order
        for the observer to actually be removed.

        """

        raise NotImplementedError()


## Function tracking argument cells
_track_argument = None

def track_argument(arg):
    """Track the cell `arg` as a dependency.

    If a cell dependency tracker, registered with `with_tracker`, is in
    effect it is called with `arg`.

    """

    if _track_argument is not None:
        _track_argument(arg)

def call_with_tracker(tracker, fn):
    """Call `fn` with a cell dependency `tracker` in effect.

    `tracker` is called whenever the value of a cell is referenced, by
    calling the cell object, within the function `fn`.

    """

    prev = _track_argument

    try:
        _track_argument = tracker

        return fn()

    finally:
        _track_argument = prev

def with_tracker(tracker):
    """Install a cell dependency `tracker` to be in effect within the decorated function."""

    def wrapper(fn):
        return call_with_tracker(tracker, fn)

    return wrapper

def without_tracker(fn):
    """Ensure that no cell dependency tracker is in effect within the decorated function `fn`."""

    return call_with_tracker(None, fn)
