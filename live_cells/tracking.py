class ArgumentTracker:
    """Installs a tracker for a given managed scope.

    This class is intended to be used with `with` to install a cell
    argument tracker for the given managed scope:

    Example:

    ```
    def track_arg(arg):
        print(f'Used: {arg}')

    with ArgumentTracker(track_arg):
       ....
    ```

    The argument tracker function is called whenever the value of a
    cell is referenced with the function call syntax.

    The previous tracker function is restored when exiting the scope.

    """

    ## Function tracking argument cells
    _track_argument = None

    @classmethod
    def track(cls, arg):
        """Track the cell `arg` as a dependency.

        If a cell dependency tracker, registered with `with_tracker`, is in
        effect it is called with `arg`.

        """

        if cls._track_argument is not None:
            cls._track_argument(arg)

    def __init__(self, tracker):
        """Create an `ArgumentTracker` that install `tracker` as the track argument function."""

        self._tracker = tracker

    def __enter__(self):
        self._previous = ArgumentTracker._track_argument
        ArgumentTracker._track_argument = self._tracker

    def __exit__(self, exception_type, exception_value, exception_traceback):
        ArgumentTracker._track_argument = self._previous

def with_tracker(tracker):
    """Install a cell dependency `tracker` to be in effect within the decorated function.

    `tracker` is the function that is installed as the cell dependency
    tracker. It is called when the value of a cell is accessed using
    the function call syntax, within the decorated function, and is
    passed the same arguments as were passed to the decorated
    function. The referenced argument cell is provided after the last
    positional argument, and before the first keyword argument.

    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            with ArgumentTracker(lambda a: tracker(*args, a, **kwargs)):
                return fn(*args, **kwargs)

        return wrapper

    return decorator

def without_tracker(fn):
    """Ensure that no cell dependency tracker is in effect within the decorated function `fn`."""

    def wrapper(*args, **kwargs):
        with ArgumentTracker(None):
            return fn(*args, **kwargs)

    return wrapper
