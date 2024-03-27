import pytest

from live_cells import value

def test_constant_cell_int_value():
    """Test that the value of the cell is equal to the value given to the constructor."""

    c = value(10)
    assert c.value == 10

def test_constant_cell_string_value():
    """Test that the value of the cell is equal to the value given to the constructor."""

    c = value('Hello World')
    assert c.value == 'Hello World'

def test_compares_equal():
    """Test that constant cells compare == when holding the same value."""

    a = value(1)
    b = value(1)

    assert a == b
    assert hash(a) == hash(b)

def test_compares_not_equal():
    """Test that constant cells compare != when holding different values."""

    a = value(1)
    b = value(2)

    assert a != b
    assert a == a
