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

The computation of a computed cell's value can be aborted using
:any:`live_cells.none`. When :any:`live_cells.none` is called inside a
computed cell, the value computation function is exited and the cell's
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

Cells provide two utility methods, ``on_error`` and ``error`` for
handling exceptions thrown in computed cells.

The ``on_error`` method creates a cell that selects the value of
another cell when an exception is thrown.

.. code-block:: python

   import live_cells as lc

   text = lc.mutable('0')
   m = lc.mutable(2)

   n = lc.computed(lambda: int(text()))

   result = n.on_error(m)

   str.value = '3'
   print(result.value) # Prints 3

   str.value = 'not a number'
   print(result.value) # Prints 2

``on_error`` accepts an optional ``type`` argument. When a non-None
``type`` is given only exceptions of the given type are handled.

.. code-block:: python

   result = n.on_error(m, type=ValueError)

The validation logic in the previous example can be implemented more
succinctly using:

.. code-block:: python

   import live_cells as lc

   text = lc.mutable('0')
   n = lc.computed(lambda: int(text()))

   is_valid = (n > lc.value(0)).on_error(lc.value(False))
   
The ``error`` method creates a cell that holds the last exception that
was raised or ``None`` if no exception has been raised:

.. code-block:: python

   error = n.error()

   @lc.watch
   def watch_errors():
       if error() is not None:
           print(f'Error: {error()}')

Like ``on_error`` this method also accepts a ``type`` argument. When
this argument is given, the cell evaluates to the exception raised
only if it is of the given exception type.

.. code-block:: python

   parse_error = n.error(type=ValueError)


``error`` also accepts an ``all`` argument. When this is ``True``, the
value of the *error* cell resets to ``None`` if the value of the cell
on which ``error`` is called changes its value such that it no longer
raises an exception. If ``all`` is ``False`` (the default), the value
of the *error* does not change if the cell on which ``error`` is
called does not raise an exception.

The difference between the two is demonstrated with the following
example:

.. code-block:: python

   import live_cells as lc
		
   text = mutable('0')
   n = lc.computed(lambda: int(text()))
		
   e1 = n.error() # all=False
   e2 = n.error(all=True)

   @lc.watch
   def watch_errors():
       print(f'\ntext = "{text()}")
       print(f'error(all=False): {e1() is None}')
       print(f'error(all=True): {e2() is None}')
   
   text.value = 'not a number'
   text.value = '10'

This results in the following being printed:

.. code-block:: text

   text = "0"
   error(all=False): True
   error(all=True): True

   text = "not a number"
   error(all=False): False
   error(all=True): False

   text = "10"
   error(all=False): False
   error(all=True): True

=============
Peeking Cells
=============

If you want to use the value of a cell in a computed cell but don't
want changes in the cells value triggering a recomputation, access the
cell via the ``peek`` property.

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(0)
   b = lc.mutable(1)

   c = lc.computed(lambda: a() + b.peek())

   lc.watch(lambda: print(f'{c()}'))

   a.value = 3 # Prints: 4
   b.value = 5 # Doesn't print anything
   a.value = 7 # Prints: 13

In this example ``c`` is a computed cell that references the value of
``a`` and *peeks* the value of ``b``. Changing the value of ``a``
causes the value of ``c`` to be recomputed, and hence the watch
function is called. However, changing the value of ``b`` does not
cause the value of ``c`` to be recomputed due to the value being
accessed via the ``peek`` property.

.. note::

   ``peek`` is a property that returns a cell:

   .. code-block:: python

      b = lc.mutable(1)
      peek_b = b.peek

      print(peek_b.value) # Prints 1

You may be asking why do we need ``peek`` instead of just accessing
the value of ``b`` directly using ``b.value``. The reason for this is
due to the cell lifecycle. Cells are only active when they have at
least one observer.

When a cell is active it recomputes its value in response to changes
in the values of its argument cells, if any. When a cell is inactive,
it does not recompute it's value when the values of its argument cells
change. This means the value of a cell may no longer be current if it
doesn't have at least one observer.

The ``peek`` property returns a cell that takes care of observing the
peeked cell, so that it remains active, but at the same prevents the
observers, added through the cell returned by ``peek``, from being
notified when its value changes.
