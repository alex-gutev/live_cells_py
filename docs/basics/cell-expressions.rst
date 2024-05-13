Cell Expressions
================

This library provides a number of tools for building expressions of
cells without requiring a computed cell to be created explicitly with
:any:`live_cells.computed`.

==========     
Arithmetic
==========

The following arithmetic and relational operators/functions can be
applied directly on cells: ``<``, ``<=``, ``>``, ``>=``, ``+``, ``-``,
unary ``-``, unary ``+``, ``*``, ``@``, ``/``, ``//``, ``%``,
``divmod``, ``**``, ``<<``, ``>>``, ``&``, ``|``, ``^``, ``~``,
``abs``, ``round``, ``math.trunc``, ``math.floor``, ``math.ceil``.

Each operator returns a cell that applies the operator on the values
of the operand cells. This allows a computed cell to be defined
directly as an expression of cells. For example the following defines
a cell that computes the sum of two cells directly using the ``+``
operator:

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(1)
   b = lc.mutable(2)

   c = a + b

   print(c.value) # Prints 3


.. note::

   This definition of the cell ``c`` is not only simpler than the
   equivalent definition using :any:`live_cells.computed` but is also
   more efficient since the argument cells are known ahead of time.

``c`` is a cell like any other cell. It can be observed by a watch
function or it can appear as an argument in a computed cell.

.. code-block:: python

   lc.watch(lambda: print(c()))

   a.value = 5 # Prints 7
   b.value = 4 # Prints 9

Expressions of cells can be arbitrarily complex:

.. code-block:: python

   x = a * b + c / d
   y = x < e

.. hint::

   To include a constant value in a cell expression, convert it to a
   cell using :any:`live_cells.value`


===================
Logic and Selection
===================

The following methods are provided by all cell objects:

``a.logand(b)``

   Creates a cell that evaluates to the logical **and** of ``a`` and ``b``.

``a.logor(b)``

   Create a cell that evaluates to the logical **or** of ``a`` and ``b``.

``a.lognot()``

   Create a cell that evaluates to the logical **not** of ``a``.

``a.select(b, c)``

   Create a cell that evaluates to the value of ``b`` if ``a`` is
   ``True`` or ``c`` if ``a`` is ``False``.

.. note::

   ``logand`` and ``logor`` are short-circuting, which means the value
   of the second operand cell is not referenced if the result of the
   expression is already known without it.

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(False)
   b = lc.mutable(False)

   c = lc.mutable(1)
   d = lc.mutable(2)
   
   cond = a.logor(b)
   cell = cond.select(c, d)

   lc.watch(lambda: print(f'{cell()}'))

   a.value = True  # Prints 1
   a.value = False # Prints 2
       

The second argument to ``select`` can be omitted, in which case the
cell's value will not be updated if the condition is ``False``.

.. code-block:: python

   import live_cells as lc

   cond = lc.mutable(False)
   a = lc.mutable(1)
		
   cell = cond.select(a)

   lc.watch(lambda: print(f'{cell()}'))

   cond.value = True  # Prints 1
   a.value = 2        # Prints 2

   cond.value = False # Prints 2
   a.value = 4        # Prints 2
   
======================
Aborting a computation
======================

The computation of the value of a computed cell can be aborted using
:any:`live_cells.none`. When :any:`live_cells.none` is called inside a
computed cell, the computation of the cell's value is aborted and its
current value is preserved. This can be used to prevent a cell's value
from being recomputed when a condition is not met.

.. note::

   The ``select`` method from the previous section uses
   :any:`live_cells.none` to retain its current value when the
   condition is ``False``.

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(4)
   b = lc.computed(lambda: a() if a() < 10 else lc.none())

   lc.watch(lambda: print(f'{b()}')
   
   a.value = 6  # Prints 6
   a.value = 15 # Prints 6
   a.value = 8  # Prints 8

If :any:`live_cells.none` is called while computing the initial value
of the cell, the cell is initialized to the value provided in the
argument to :any:`live_cells.none`, which defaults to ``None`` if no
argument is given.

.. attention::

   The value of a computed cell is only computed if it is actually
   referenced. :any:`live_cells.none` only preserves the current value
   of the cell, but this might not be the latest value of the cell if
   the cell is only referenced conditionally. A good rule of thumb is
   to use :any:`live_cells.none` only to prevent a cell from holding
   an invalid value.


==================
Exception handling
==================

When an exception is thrown while computing the value of a cell, it is
rethrown when the cell's value is referenced. This allows exceptions
to be handled using ``try`` and ``except`` inside computed cells.

.. code-block:: python

   import live_cells as lc

   text = lc.mutable('0')
   n = lc.computed(lambda: int(text()))

   @lc.computed
   def is_valid():
       try:
           return n() > 0

       except:
           return False

   print(is_valid.value) # Prints False

   text.value = '5'
   print(is_valid.value) # Prints True

   text.value = 'not a number'
   print(is_value.value) # Prints False
