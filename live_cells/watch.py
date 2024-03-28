from .tracking import ArgumentTracker

class CellWatcher:
    """Maintains the state of a cell watch function."""

    def __init__(self, callback):
        """Create and start a cell watch function.

        `callback` is called once immediately, with no arguments, to
        determine the cells that are referenced by it.

        Afterwards `callback` is called whenever at least one of the
        cells referenced within it change, until `stop()` is called.

        """
        self.callback = callback
        self.observer = CellWatchObserver(callback)

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

    def __init__(self, callback):
        """Create a watch function observer for watch function `callback`."""

        self.callback = callback

        self.arguments = set()
        self.updating = False

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
        """Call the watch function."""

        try:
            with ArgumentTracker(self.track_argument):
                self.callback()

        except:
            # TODO: Print to log
            pass


    # Cell Observer Methods

    def will_update(self, cell):
        if not self.updating:
            self.updating = True

    def update(self, cell):
        if self.updating:
            self.updating = False

            # TODO: Schedule after current update cycle
            self.call_watch()

def watch(callback):
    """Register `callback` as a cell watch function.

    `callback` (A function of no arguments) is called once immediately
    to determine the cells referenced within it. It is then called
    again whenever the values of the cells referenced within it
    change.

    To stop `callback` from being called for further changes to the
    cell values, call the `.stop()` method on the object returned by
    this function.

    This function may be used as a decorator.

    """

    return CellWatcher(callback)
