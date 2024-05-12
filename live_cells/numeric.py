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

@cell_extension
@cell_function
def __add__(a, b):
    return op.add(a, b)

@cell_extension
@cell_function
def __sub__(a, b):
    return op.sub(a, b)

@cell_extension
@cell_function
def __mul__(a, b):
    return op.mul(a, b)

@cell_extension
@cell_function
def __matmul__(a, b):
    return op.matmul(a, b)

@cell_extension
@cell_function
def __truediv__(a, b):
    return op.truediv(a, b)

@cell_extension
@cell_function
def __floordiv__(a, b):
    return op.floordiv(a, b)

@cell_extension
@cell_function
def __mod__(a, b):
    return op.mod(a, b)

@cell_extension
@cell_function
def __divmod__(a, b):
    return divmod(a, b)

@cell_extension
@cell_function
def __pow__(a, n):
    return op.pow(a, n)

@cell_extension
@cell_function
def __lshift__(a, n):
    return op.lshift(a, n)

@cell_extension
@cell_function
def __rshift__(a, n):
    return op.rshift(a, n)

@cell_extension
@cell_function
def __and__(a, b):
    return op.and_(a, b)

@cell_extension
@cell_function
def __xor__(a, b):
    return op.xor(a,b)

@cell_extension
@cell_function
def __or__(a, b):
    return op.or_(a, b)

@cell_extension
@cell_function
def __neg__(a):
    return op.neg(a)

@cell_extension
@cell_function
def __pos__(a):
    return op.pos(a)

@cell_extension
@cell_function
def __abs__(a):
    return abs(a)

@cell_extension
@cell_function
def __invert__(a):
    return op.invert(a)

@cell_extension
@cell_function
def __round__(a, ndigits=None):
    return round(a, ndigits)

@cell_extension
@cell_function
def __trunc__(a):
    return math.trunc(a)

@cell_extension
@cell_function
def __floor__(a):
    return math.floor(a)

@cell_extension
@cell_function
def __ceil__(a):
    return math.ceil(a)
