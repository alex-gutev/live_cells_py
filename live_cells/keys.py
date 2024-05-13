class ValueKey:
    """A cell key which is distinguished from other keys by one or more values.

    Instances of this class compare equal to other instances if they
    have the same runtime type and the `args` of both instances,
    provided during construction, compare equal.

    """

    def __init__(self, *args):
        """Create a key distinguished from other keys by the values in `args`."""

        self.args = args

    def __eq__(self, other):
        if type(self) == type(other):
            return self.args == other.args

        return NotImplemented

    def __hash__(self):
        return hash(self.args)
