class CountTestObserver:
    """A cell observer that counts how many times its methods are called.

    `count_will_update` is the number of times `will_update` was
    called.

    `count_update` is the number of times `update` was called.

    """

    def __init__(self):
        self.count_will_update = 0
        self.count_update = 0

    def update(self, cell):
        self.count_update += 1

    def will_update(self, cell):
        self.count_will_update += 1

class ValueTestObserver:
    """A cell observer that records the values of the observed cell in a list.

    This observer records the value of the observed cell(s), in the
    list `values`, at every call to `update`.

    NOTE: Duplicate values are not recorded in `values`.

    """

    def __init__(self):
        self.values = []

    def will_update(self, cell):
        pass

    def update(self, cell):
        try:
            value = cell.value

            if not self.values or self.values[-1] != value:
                self.values.append(value)

        except:
            pass
