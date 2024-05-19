Cells
=====

A cell is an object with a value and a set of observers that react to
changes in its value. You'll see exactly what that means in a moment.

There are a number of ways to create cells. The simplest cell is the
constant cell, created with the :any:`live_cells.value` function,
which holds a constant value.

.. code-block:: python

   import live_cells as lc

   a = lc.value(1)
   b = lc.value('hello world')


=============
Mutable Cells
=============

Mutable cells, created with :any:`live_cells.mutable`, which takes
the initial value of the cell, have a `value` property that can be set
directly.

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(0)

   print(a.value) # Prints 0

   # Set the value of a to 3
   a.value = 3
   print(a.value) # Prints 3

===============
Observing Cells
===============

When the value of a cell changes, its observers are notified of the
change. The simplest way to demonstrate this is to set up a *watch
function* using :any:`live_cells.watch`:

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(0)
   b = lc.mutable(1)

   lc.watch(lambda: print(f'{a()}, {b()}'))

   a.value = 5  # Prints 5, 1
   b.value = 10 # Prints 5, 10

:any:`live_cells.watch` takes a watch function and registers it to be
called when the values of the cells referenced within it change. In
the example above, a watch function that prints the values of cells
``a`` and ``b`` is defined. This function is called automatically when the
value of either ``a`` or ``b`` changes.

There are a couple of points to keep in mind when using :any:`live_cells.watch`:

* The watch function is called once immediately when
  :any:`live_cells.watch` is called, to determine which cells are
  referenced by it.

* :any:`live_cells.watch` automatically tracks which cells are
  referenced within the watch function and calls it when their values
  change. This works even when the cells are referenced conditionally.

.. attention::

   Within a watch function, the values of cells are referenced using
   the function call syntax, e.g. ``a()``, rather than accessing the
   ``value`` property directly.

Every call to :any:`live_cells.watch` adds a new watch function:

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(0)
   b = lc.mutable(1)

   lc.watch(lambda: print(f'{a()}, {b()}'))
   lc.watch(lambda: print(f'A = {a()}'))

   # Prints: 20, 1
   # Also prints: A = 20
   a.value = 20

   # Prints 20, 10
   b.value = 10

This results in the following being printed:

.. code-block:: text

  20, 1
  A = 20
  20, 20

In this example, the second watch function only observes the value of
``a``. Change the value of ``a`` results in both the first and second
watch function being called. Changing the value of ``b`` results in
only the first watch function being called, since the second watch
function does not reference ``b`` and hence is not observing it.

:any:`live_cells.watch` returns a watch *handle* (:any:`CellWatcher`),
which provides a ``stop`` method that *deregisters* the watch
function. When the ``stop`` method is called, the watch function is no
longer called when the values of the cells it is observing change.

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(0)

   watcher = lc.watch(lambda: print(f'A = {a()}'))

   # Prints A = 1
   a.value = 1

   # Prints A = 2
   a.value = 2

   watcher.stop()

   # Doesn't print anything
   a.value = 3


.. tip::

   A watch function with more than one expression can be defined by
   using :any:`live_cells.watch` as a decorator:

   .. code-block:: python

      import live_cells as lc

      a = lc.mutable(0)

      @lc.watch
      def watcher():
          print(f'A = {a()}')
	  print(f'A + 1 = {a() + 1}')

      # Prints:
      #   A = 2
      #   A + 1 = 3
      
      a.value = 2

  The decorated function is registered as a watch function that
  observes the cells referenced within it. The watch handle can be
  accessed by the name of the decorated function. For example, the
  watch function in the previous example can be stopped with the
  following:

  .. code-block:: python

     watcher.stop()

:any:`live_cells.watch` also takes an optional ``schedule`` argument,
which if not *None* is a function that is called when the watch
function should be called, with the watch callback passed as an
argument. The ``schedule`` function should *schedule* the callback
function to it, to be called at a later stage. If ``schedule`` is
*None*, the watch function is called immediately when the cells
referenced within it change.

.. code-block:: python

   import gevent
   import live_cells as lc

   a = lc.mutable()

   @lc.watch(schedule=gevent.spawn)
   def watch():
       print(f'{a()}')

In this example a watch function observing cell ``a`` is defined. When
the value of ``a`` changes, the watch function is not called
immediately but is scheduled to run on a `gevent
<http://www.gevent.org/>`_ green thread, using ``gevent.spawn``.

.. important::

   The watch function sees the values of the cells, which are
   referenced within it, as they are at the time the ``schedule``
   function is called and not at the time when the watch function is
   actually run. This guarantees that the watch function will not
   "miss" updates if it runs after the values of the cells are changed
   again.

==============
Computed Cells
==============

A *computed cell* is a cell with a value that is defined as a function
of the values of one or more argument cells. Whenever the value of an
argument cell changes, the value of the computed cell is recomputed.

Computed cells are defined using :any:`live_cells.computed`, which
takes the value computation function of the cell:

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(1)
   b = lc.mutable(2)

   sum = lc.computed(lambda: a() + b())

In this example, ``sum`` is a computed cell with the value defined as
the sum of cells ``a`` and ``b``. The value of ``sum`` is recomputed
whenever the value of either ``a`` or ``b`` changes. This is
demonstrated below:

.. code-block:: python

   lc.watch(lambda: print(f'The sum is {sum()}'))

   a.value = 3 # Prints: The sum is 5
   b.value = 4 # Prints: The sum is 7

In this example:

#. A watch function observing the ``sum`` cell is defined.
#. The value of ``a`` is set to ``3``, which:

   #. Causes the value of ``sum`` to be recomputed.
   #. Calls the watch function defined in 1.

#. The value of ``b`` is set to ``4``, which likewise also results in
   the value of ``sum`` being recomputed and the watch function being
   called.

.. tip::

   A computed cell with more than one expression can be defined by
   using :any:`live_cells.computed` as a decorator:


   .. code-block:: python

      import live_cells as lc

      n = lc.mutable(2)

      @lc.computed
      def factorial_n():
          result = 1

	  while n() > 1:
	    result *= n
	    n -= 1
	  
	  return result

      lc.watch(lambda: print(f'n! = {factorial_n()}'))

   The computed cell is defined with the decorated function as the
   compute function. The cell can then be referenced using the name of
   the decorated function.

The :any:`live_cells.computed` function takes a ``changes_only``
argument which allows you to control whether the computed cell
notifies its observers if its value hasn't changed after a
recomputation. By default this is ``False``, which means the computed
cell notifies its observers whenever it is recomputed. If
``changes_only`` is ``True``, the cell only notifies its observers if
the new value of the cell is not equal to its previous value.

This is demonstrated with the following example:

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(0)
   b = lc.computed(lambda: a % 2, changes_only=True)

   lc.watch(lambda: print(f'{b()}'))

   a.value = 1
   a.value = 3
   a.value = 5
   a.value = 6
   a.value = 8

This results in the following being printed to standard output:

.. code-block:: text

   0
   1
   0

Notice that only three lines are printed to standard output, even
though the value of the computed cell argument ``a`` was changed five
times.

If ``changes_only=True`` is omitted from the definition of ``b``, the
following is printed to standard output:

.. code-block:: text

   0
   1
   1
   1
   0
   0

Notice that a new line is printed to standard output whenever the
value of ``a``, which is an argument of ``b`` is changed. This is
because ``b`` notifies its observers whenever the value of its
argument ``a`` has changed, even if ``b``\ 's new value is equal to
its previous value.
   
=============
Batch Updates
=============

The values of multiple mutable cells can be set simultaneously in a
*batch update*. The effect of this is that while the values of the
cells are changed on setting the ``value`` property, the observers of
the cells are only notified after all the cell values have been set.

Batch updates are performed using the :any:`live_cells.batch` context
manager:

.. code-block:: python

   import live_cells as lc

   a = lc.mutable(0)
   b = lc.mutable(1)

   lc.watch(lambda: print(f'a = {a()}, b = {b()}'))

   # This only prints: a = 15, b = 3
   with lc.batch():
       a.value = 15
       b.value = 3

In the example above, the values of ``a`` and ``b`` are set to ``15``
and ``3`` respectively, with a *batch update*. The watch function,
which observes both ``a`` and ``b`` is only called once when exiting
the context managed by :any:`live_cells.batch`.

As a result the following is printed:

.. code-block:: text

   a = 0, b = 1
   a = 15, b = 3

#. ``a = 0, b = 1`` is printed when the watch function is first defined.
#. ``a = 15, b = 3`` is printed when exiting the context managed by
   :any:`live_cells.batch`.
