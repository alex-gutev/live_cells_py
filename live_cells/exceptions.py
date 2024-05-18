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
