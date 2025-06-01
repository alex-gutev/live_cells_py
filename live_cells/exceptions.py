class StopComputeException(Exception):
    """Exception used to indicate that the cell's value should not be computed.

    When this exception is raised inside the value computation
    function of a cell, the cell's value is not updated. Instead the
    cell's current value is preserved.

    :param default_value: The value to initialize the cell to, if this
                          exception is thrown while computing the
                          initial value of the cell.

    """

    def __init__(self, default_value=None):
        self.default_value = default_value

        super().__init__("StopComputeException() raised. If you're seeing this you most likely"
                         ' used none() outside a cell value computation function.')

class UninitializedCellError(Exception):
    """Exception raised when accessing the value of a cell before it is initialized."""

    def __init__(self):
        super().__init__('The value of a cell was referenced before it was initialized.')

class PendingAsyncValueError(Exception):
    """Exception raised when accessing the value of an async cell before the coroutine has completed."""

    def __init__(self):
        super().__init__('The value of an async cell was referenced before the async task has completed.')
