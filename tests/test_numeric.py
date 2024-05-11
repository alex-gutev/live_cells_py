import pytest

from math import isclose, trunc, floor, ceil
from live_cells import value, mutable

class Wrapper:
    """Wraps a value provides definitions for certain numeric operators."""

    def __init__(self, value):
        self.value = value

    def __matmul__(self, other):
        return Wrapper(self.value * other.value)

    def __pos__(self):
        return Wrapper(self.value + 5)

class TestNumericExtension:
    """Tests numeric operators applied on cells."""

    def test_add(self):
        a = value(5)
        b = mutable(6)

        c = a + b

        assert c.value == 11

        b.value = 10
        assert c.value == 15

    def test_sub(self):
        a = mutable(13)
        b = value(20)

        c = a - b

        assert c.value == -7

        a.value = 50
        assert c.value == 30

    def test_mul(self):
        a = mutable(10)
        b = value(8)

        c = a * b

        assert c.value == 80

        a.value = 20
        assert c.value == 160

    def test_matmul(self):
        a = mutable(Wrapper(10))
        b = value(Wrapper(8))

        c = a @ b

        assert c.value.value == 80

        a.value = Wrapper(20)
        assert c.value.value == 160

    def test_truediv(self):
        a = mutable(7)
        b = value(2)

        c = a / b

        assert isclose(c.value, 3.5)

        a.value = 10
        assert c.value == 5

    def test_floordiv(self):
        a = mutable(7)
        b = value(2)

        c = a // b

        assert c.value == 3

        a.value = 11
        assert c.value == 5

    def test_mod(self):
        a = mutable(17)
        b = value(3)

        c = a % b

        assert c.value == 2

        a.value = 21
        assert c.value == 0

    def test_divmod(self):
        a = mutable(17)
        b = value(3)

        c = divmod(a, b)

        assert c.value == (5, 2)

        a.value = 21
        assert c.value == (7, 0)

    def test_pow(self):
        a = mutable(3)
        b = value(3)

        c = a ** b

        assert c.value == 27

        a.value = 4
        assert c.value == 64

    def test_lshift(self):
        a = mutable(21)
        b = value(2)

        c = a << b

        assert c.value == 84

        a.value = 43
        assert c.value == 172

    def test_rshift(self):
        a = mutable(21)
        b = value(2)

        c = a >> b

        assert c.value == 5

        a.value = 43
        assert c.value == 10

    def test_and(self):
        a = mutable(19)
        b = value(7)

        c = a & b

        assert c.value == 3

        a.value = 21
        assert c.value == 5

    def test_or(self):
        a = mutable(19)
        b = value(7)

        c = a | b

        assert c.value == 23

        a.value = 11
        assert c.value == 15

    def test_xor(self):
        a = mutable(19)
        b = value(7)

        c = a ^ b

        assert c.value == 20

        a.value = 11
        assert c.value == 12

    def test_neg(self):
        a = mutable(10)
        b = -a

        assert b.value == -10

        a.value = -19
        assert b.value == 19

    def test_pos(self):
        a = mutable(Wrapper(10))
        b = +a

        assert b.value.value == 15

        a.value = Wrapper(-20)
        assert b.value.value == -15

    def test_abs(self):
        a = mutable(-10)
        b = abs(a)

        assert b.value == 10

        a.value = 15
        assert b.value == 15

    def test_invert(self):
        a = mutable(10)
        b = ~a

        assert b.value == -11

        a.value = -19
        assert b.value == 18

    def test_round(self):
        a = mutable(10.5167)
        b = round(a)
        c = round(a, value(2))

        assert isclose(b.value, 11)
        assert isclose(c.value, 10.52)

        a.value = 2.056

        assert isclose(b.value, 2)
        assert isclose(c.value, 2.06)

    def test_trunc(self):
        a = mutable(10.78)
        b = trunc(a)

        assert isclose(b.value, 10)

        a.value = -2.56

        assert isclose(b.value, -2)

    def test_floor(self):
        a = mutable(10.78)
        b = floor(a)

        assert isclose(b.value, 10)

        a.value = -2.06

        assert isclose(b.value, -3)

    def test_ceil(self):
        a = mutable(10.078)
        b = ceil(a)

        assert isclose(b.value, 11)

        a.value = -2.6

        assert isclose(b.value, -2)
