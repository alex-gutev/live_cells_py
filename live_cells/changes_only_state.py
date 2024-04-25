class ChangesOnlyState:
    """ComputeCellState mixin that adds checks for whether the cell's value has changed.

    This mixin implements did_change by comparing the new value of the
    cell to its previous value using `==`. Additionally, this state
    also converts a lazy cell to an eager cell since it is necessary
    to compute the value of the cell at every update.

    """

    def __init__(self, cell, key=None):
        super().__init__(
            cell = cell,
            key = key
        )

        self._has_value = False
        self._old_value = None

    def did_change(self):
        try:
            return not self._has_value or self.cell.value != self._old_value

        except:
            return True

    def pre_update(self):
        super().pre_update()

        try:
            self._has_value = True
            self._old_value = self.cell.value

        except:
            self._has_value = False

    def post_update(self):
        super().post_update()

        self._has_value = False
        self._old_value = None
