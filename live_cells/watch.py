from .tracking import ArgumentTracker
from .exceptions import StopComputeException

class CellWatcher:
    """Maintains the state of a cell watch function."""

    def __init__(self, callback, schedule=None):
        """Create and start a cell watch function.

        `callback` is called once immediately, with no arguments, to
        determine the cells that are referenced by it.

        Afterwards `callback` is called whenever at least one of the
        cells referenced within it change, until `stop()` is called.

        `schedule` is an optional function which is called with the
        callback function provided as an argument. When `schedule` is
        called, it should schedule the callback function provided to
        it to be called.

        """

        self.callback = callback
        self.observer = CellWatchObserver(callback, schedule=schedule)

    def stop(self):
        """Stop the watch function from being called for future updates.

        The watch callback will not be called again after this method
        is called.

        """

        self.observer.stop()

    def __call__(self):
        """Register the watch function.

        This is useful to restart a watch function that was stopped by
        calling stop().

        """

        self.callback()

class CellWatchObserver:
    """Watch function cell observer."""

    def __init__(self, callback, schedule=None):
        """Create a watch function observer for watch function `callback`.

        `schedule` is an optional function which is called with the
        callback function provided as an argument. When `schedule` is
        called, it should schedule the callback function provided to
        it to be called.

        """

        self.callback = callback
        self.schedule = schedule

        self.arguments = set()
        self.updating = False

        self.waiting_for_change = False

        self.call_watch()

    def stop(self):
        """Remove the observer from the watched cells."""

        for arg in self.arguments:
            arg.remove_observer(self)

        self.arguments.clear()


    def track_argument(self, arg):
        """Track cell `arg` as a dependency of the watch function."""

        if arg not in self.arguments:
            arg.add_observer(self)
            self.arguments.add(arg)

    def call_watch(self):
        """Call the watch function scheduling it if necessary."""

        if self.schedule:
            self.schedule(self.call_callback)

        self.call_callback()

    def call_callback(self):
        """Call the watch function."""

        try:
            with ArgumentTracker(self.track_argument):
                self.callback()

        except StopComputeException:
            # Stop execution of watch function

            pass

        except:
            # TODO: Print to log
            pass


    # Cell Observer Methods

    def will_update(self, cell):
        if not self.updating:
            self.updating = True
            self.waiting_for_change = False

    def update(self, cell, did_change):
        if self.updating or (did_change and self.waiting_for_change):
            self.updating = False
            self.waiting_for_change = not did_change

            if did_change:
                # TODO: Schedule after current update cycle
                self.call_watch()

def watch(callback=None, schedule=None):
    """Register `callback` as a cell watch function.

    `callback` (A function of no arguments) is called once immediately
    to determine the cells referenced within it. It is then called
    again whenever the values of the cells referenced within it
    change.

    To stop `callback` from being called for further changes to the
    cell values, call the `.stop()` method on the object returned by
    this function.

    `schedule` is an optional function which is called with the
    callback function provided as an argument. When `schedule` is
    called, it should schedule the callback function provided to it to
    be called.


    This function may be used as a decorator.

    """

    if callback is None:
        def decorator(fn):
            return watch(fn, schedule)

        return decorator

    return CellWatcher(callback, schedule)
