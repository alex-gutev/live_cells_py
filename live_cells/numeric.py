import math
import functools
import operator as op

from .cell import Cell
from .compute_cell import ComputeCell

def cell_function(compute=None):
    """Create a function that is applied on cells and returns a new cell.

    This transform the function `compute` into a function that accepts
    cells as arguments and returns a new ComputeCell which evaluates
    to `compute` applied on the values of the argument cells.

    Can be used a decorator.

    """

    if compute is None:
        def decorator(fn):
            return cell_function(fn)

        return decorator

    @functools.wraps(compute)
    def wrapper(*args):
        return ComputeCell(lambda: compute(*(arg.value for arg in args)), set(args))

    return wrapper

def cell_extension(fn = None, name=None):
    """Add `fn` as a method to all cell objects.

    `fn` is added as a method to the Cell class under the given `name`
    or the name of `fn` if `name` is None.

    This function may be used as a decorator.

    """

    if fn is None:
        def decorator(fn):
            return cell_extension(fn, name)

        return decorator

    setattr(Cell, name if name is not None else fn.__name__, fn)

    return fn

@cell_extension
@cell_function
def __lt__(a, b):
    return op.lt(a, b)

@cell_extension
@cell_function
def __le__(a, b):
    return op.le(a, b)

@cell_extension
@cell_function
def __gt__(a, b):
    return op.gt(a, b)

@cell_extension
@cell_function
def __ge__(a, b):
    return op.ge(a, b)

@cell_function
def add(a, b):
    return op.add(a, b)

@cell_function
def sub(a, b):
    return op.sub(a, b)

@cell_function
def mul(a, b):
    return op.mul(a, b)

@cell_function
def matmul(a, b):
    return op.matmul(a, b)

@cell_function
def truediv(a, b):
    return op.truediv(a, b)

@cell_function
def floordiv(a, b):
    return op.floordiv(a, b)

@cell_function
def mod(a, b):
    return op.mod(a, b)

@cell_function
def cell_divmod(a, b):
    return divmod(a, b)

@cell_function
def cell_pow(a, n):
    return op.pow(a, n)

@cell_function
def lshift(a, n):
    return op.lshift(a, n)

@cell_function
def rshift(a, n):
    return op.rshift(a, n)

@cell_function
def cell_and(a, b):
    return op.and_(a, b)

@cell_function
def cell_xor(a, b):
    return op.xor(a,b)

@cell_function
def cell_or(a, b):
    return op.or_(a, b)

@cell_function
def neg(a):
    return op.neg(a)

@cell_function
def pos(a):
    return op.pos(a)

@cell_function
def cell_abs(a):
    return abs(a)

@cell_function
def invert(a):
    return op.invert(a)

@cell_function
def cell_round(a, ndigits=None):
    return round(a, ndigits)

@cell_function
def cell_trunc(a):
    return math.trunc(a)

@cell_function
def cell_floor(a):
    return math.floor(a)

@cell_function
def cell_ceil(a):
    return math.ceil(a)

Cell.__add__ = add
Cell.__sub__ = sub
Cell.__mul__ = mul
Cell.__matmul__ = matmul
Cell.__truediv__ = truediv
Cell.__floordiv__ = floordiv
Cell.__mod__ = mod
Cell.__divmod__ = cell_divmod
Cell.__pow__ = cell_pow
Cell.__lshift__ = lshift
Cell.__rshift__ = rshift
Cell.__and__ = cell_and
Cell.__xor__ = cell_xor
Cell.__or__ = cell_or
Cell.__neg__ = neg
Cell.__pos__ = pos
Cell.__abs__ = cell_abs
Cell.__invert__ = invert
Cell.__round__ = cell_round
Cell.__trunc__ = cell_trunc
Cell.__floor__ = cell_floor
Cell.__ceil__ = cell_ceil
