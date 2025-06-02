from contextvars import ContextVar

class ArgumentTracker:
    """Context manager that installs an argument tracker for a given context.

    The function ``tracker`` is called whenever a cell is referenced,
    with the function call syntax, within the context managed by the
    ArgumentTracker. The referenced cell is passed as an argument.

    The previous tracker function is restored when exiting the context.

    .. code-block::

       def track_arg(arg):
           print(f'Used: {arg}')

       with ArgumentTracker(track_arg):
           ....


    :param tracker: A function of one argument, called when a cell is
                    referenced.

    :type tracker: function

    :param override: If true the ``tracker`` function can also
                     override the values of the referenced cells by
                     returning a new value for the cell.

    :type override: bool

    """

    ## Function tracking argument cells
    _tracker = ContextVar('argument_tracker', default=None)

    @classmethod
    def track(cls, arg):
        """Track the cell `arg` as a dependency.

        If a cell dependency tracker, registered with `with_tracker`, is in
        effect it is called with `arg`.

        """

        tracker = cls._tracker.get()

        if tracker is not None:
            return tracker(arg)

        return arg.value

    def __init__(self, tracker, override=False):
        def track_fn(cell):
            tracker(cell)
            return cell.value

        self._track_fn = tracker if (override or tracker is None) else track_fn

    def __enter__(self):
        self._token = ArgumentTracker._tracker.set(self._track_fn)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        ArgumentTracker._tracker.reset(self._token)

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
