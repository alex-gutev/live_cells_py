Integration with Asyncio
========================

There are a number of tools for integrating cells with asyncio
awaitables and coroutines.

===================
Asynchronous Cells
===================

An *asynchronous cell* is a cell with an *awaitable* value. To define a
cell that performs a computation on an asynchronously computed value,
define a computed cell with an ``async`` computation function.

.. code-block:: python

   import asyncio
   import live_cells as lc

   # Helper for creating awaitables
   async def coro1(n):
       await asyncio.sleep(5)
       return n

   n = lc.mutable(coro1(1))

   # An asynchronous computed cell
   @lc.computed
   async def next():
       return await n() + 1

* ``n`` is a mutable cell holding an *awaitable*, in this case
  returned by a coroutine function.

* ``next`` is a computed cell with a coroutine as its computation
  function that *awaits* the *awaitable* held in *n* and adds ``1`` to
  it.

* The value of ``next`` is an *awaitable* holding the result returned by
  its value computation function.

To retrieve the result computed by the ``next`` cell, ``await`` its
value:

.. code-block:: python

   print(await next()) # Prints 2
  
When a new *awaitable* is assigned to ``n``, the value of ``next`` is
recomputed.

.. code-block:: python

   n.value = coro(5)
   print(await next()) # Prints 6


.. important::

   The values of asynchronous computed cells, which are *awaitables*,
   are still updated **synchronously** whenever the values of their
   arguments change just like any other computed cell. It's only the
   computation functions themselves that are run asynchronously.

------------------
Multiple Arguments
------------------

An asynchronous computed cell can reference multiple argument cells,
just like an ordinary computed cell.

.. code-block:: python

   import asyncio
   import live_cells as lc

   async def delayed(value, *, delay=1):
       await asyncio.sleep(delay)
       return value

   a = lc.mutable(delayed(1, delay=2))
   b = lc.mutable(delayed(2, delay=5))

   @lc.computed
   async def c():
       return await a() + await b()

==========
Wait Cells
==========

A *wait cell* is a cell that retrieves the result of an *awaitable*
that is held in another cell. When the *awaitable* completes with a
value or error, the value of the *wait cell* is updated to the result
of the *awaitable*. This allows other cells and watch functions to
retrieve the result of an *awaitable* without having to use the
*await* keyword.

Wait cells are created by calling the :any:`waited` method on an
asynchronous cell, which holds an *awaitable* value:

.. code-block:: python

   import asyncio
   import live_cells as lc

   async def delayed(value, *, delay=1):
       await asyncio.sleep(delay)
       return value
   
   n = lc.mutable(delayed(1))
   wait_n = n.waited()

   @lc.computed
   def next():
       return wait_n() + 1

In this example, ``next`` is not an asynchronous computed cell and its
computation function is not a coroutine. Instead, it retrieves the
result of the *awaitable* held in ``n`` through a *wait cell* created
with ``waited``.

.. important::

   A *wait cell* must have at least one observer to wait for
   *awaitables* held in the *asynchronous cells*. If the *wait cell*
   has no observers, it neither tracks the completion of the
   *awaitables* in the *asynchronous cell* nor updates its own value.

``waited`` can be used on any cell that holds an awaitable, regardless
of whether it's a constant, mutable or computed cell. If the awaitable
completes with an exception, it is raised when accessing the value of
the *wait cell*. Similarly, exceptions raised by the cell holding the
awaitable itself, are raised when the value of the *wait cell* is
accessed.

The :any:`wait` method creates a *wait cell* and references its value
in one go. This can be used to simplify the definition of ``next``:

.. code-block:: python

   @lc.computed
   def next():
       return n.wait() + 1


.. note::

   ``n.wait()`` is equivalent to ``n.waited()()``

With the default options ``waited``/``wait`` creates a cell that has
the following behaviour:

* Accessing the value of the cell before the *awaitable* has
  completed, results in a :any:`PendingAsyncValueError` exception
  being raised.

* The value of the cell is updated to the result of the *awaitable*,
  when it completes with a value or an error.

* When the value of the *asynchronous cell*, which holds the *awaitable*,
  changes, the *wait cell* is reset, which means:

  * :any:`PendingAsyncValueError` is raised if its value is accessed
    before the new *awaitable* has completed.

  * The previous *awaitable* is ignored, and no value updates are
    emitted for it by the *wait cell* if it completes after the value
    of the *asynchronous cell* changes.

------------
Reset Option
------------
    
The ``reset`` argument controls whether the *wait cell* is reset when
the value of the asynchronous cell changes. By default, ``reset`` is
``True`` if not given, which means the *wait cell* is reset.

If ``reset`` is ``False`` the *wait cell* is not reset when the value
of the asynchronous cell changes. This means that instead of raising
:any:`PendingAsyncValueError`, the completed value or error of the
previous *awaitable* is retained until the new *awaitable* completes.

.. code-block:: python

   import asyncio
   import live_cells as lc

   async def delay(value, *, delay=1):
       await asyncio.sleep(delay)
       return value

   n = lc.mutable(delay(1))

   @lc.watch
   def watch_n():
       try:
           print(f'N = {n.wait()}')

       except PendingAsyncValueError:
           print(f'PendingAsyncValueError')

The watch function defined above, `watch_n`, access the value of the
*awaitable* held in ``n`` through a *wait cell* defined with
``reset=True``, which is the default if no ``reset`` argument is
given.

When a new *awaitable* is assigned to ``n``:

.. code-block:: python
		
   # Give the coroutine a chance to execute
   await n.value

   n.value = delay(2)

the following is printed to standard output:

.. code-block::

   PendingAsyncValueError
   N = 1
   PendingAsyncValueError
   N = 2

If the *wait cell* is created with ``reset=False`` instead:

.. code-block::

   @lc.watch
   def watch_n():
       try:
           print(f'N = {n.wait(reset=False)}')

       except PendingAsyncValueError:
           print(f'PendingAsyncValueError')

the following is printed to standard output:

.. code-block::

   PendingAsyncValueError
   N = 1
   N = 2

------------
Queue Option
------------
   
Even with ``reset=False`` the *wait cell* still only waits for the
last *awaitable* to complete.

When the value of the *asynchronous cell* changes multiple times
before the *awaitables* held in the cell have completed, a value
update is only emitted when the last *awaitable* completes.

The following:

.. code-block:: python

   n.value = delay(3)
   n.value = delay(4)
   n.value = delay(5)

only results in ``N = 5`` being printed to standard output, since the
previous two *awaitables* did not have a chance to complete.

The ``queue`` argument controls whether the *wait cell* waits for
every *awaitable* to complete or only the last *awaitable*. By default
``queue`` is ``False``, which means the *wait cell* only waits for the
last *awaitable* to complete.

If ``queue`` is ``True`` the *wait cell* waits for all *awaitables* to
complete.

.. important::

   ``queue=True`` only has an effect if ``reset=False`` is also given.

By creating the *wait cell* from the previous example with
``queue=True``:

.. code-block::

   @lc.watch
   def watch_n():
       try:
           value = n.wait(reset=False, queue=True)
           print(f'N = {value}')

       except PendingAsyncValueError:
           print(f'PendingAsyncValueError')

the following assignments to the cell holding the awaitable ``n``:

.. code-block:: python

   n.value = delay(3)
   n.value = delay(4)
   n.value = delay(5)

result in the following being printed to standard output:

.. code-block::

   N = 3
   N = 4
   N = 5

The *wait cell* waits for the *awaitables* in the same order as they
are assigned to the asynchronous cell, ``n``, which is not necessarily the
same as the order of completion of the *awaitables*.

For example the following:

.. code-block::

   n.value = delay(3, delay=10)
   n.value = delay(4, delay=1)
   n.value = delay(5, delay=3)

always results in the following being printed to standard output,
regardless of the actual order of completion of the *awaitables*:

.. code-block::

   N = 3
   N = 4
   N = 5


.. caution::

   If an asynchronous cell evaluates to an *awaitable* that never
   completes, all *wait cells* created with ``queue=True`` will be
   stuck with the completed value of the last *awaitable*, if
   any. Therefore it's best to only use ``queue=True`` if you're
   certain that all *awaitables* will complete.

------------------
Multiple Arguments
------------------

The :any:`live_cells.waited` and :any:`live_cells.wait` functions can
be used to create a *wait cell* that waits for multiple asynchronous
cells simultaneously.

:any:`live_cells.waited` takes a variable number of *asynchronous
cells* as arguments and returns a single *wait cell* that evaluates to
a list holding the completed values of the *awaitables* held in the
*asynchronous cells*. If an *asynchronous cell* raises an exception,
or an *awaitable* completes with an error, it is raised by the *wait
cell*.

:any:`live_cells.wait` takes the same arguments as
:any:`live_cells.waited` but creates the *wait cell* and
references its value in one go much like the :any:`wait` method.

.. code-block:: python

   import asyncio
   import live_cells as lc

   async def delayed(value, *, delay=1):
       await asyncio.sleep(delay)
       return value

   a = lc.mutable(delayed(1))
   b = lc.mutable(delayed(2))

   @lc.computed
   def c():
       x,y = lc.wait(a, b)

       return x + y

   @lc.watch
   def watch_sum():
       print(f'A + B = {c()}')

The cell ``c`` computes the sum of the completed values of the
*awaitables* held in the *asynchronous cells* ``a`` and ``b``. The
values of the *awaitables* are accessed through a *wait cell* that
waits for the both the *awaitable* held in ``a`` and the *awaitable*
held in ``b``, simultaneously.

.. note::

   :any:`live_cells.waited` and :any:`live_cells.wait` accept the same
   keyword arguments as :any:`waited` and :any:`wait`:
   
   .. code-block:: python
		   
      x,y = lc.wait(a, b, reset=False)

~~~~~~~~~~~~~~~~
Avoding Glitches
~~~~~~~~~~~~~~~~
      
This form should be used as opposed to multiple individual :any:`wait`
calls, since the latter may result in glitches if the *asynchronous*
cells share a common ancestor or are updated simultaneously in a batch
update. This becomes more apparent if the ``reset=False`` option is
used.

For example if the computed cell ``c`` is defined with multiple
individual calls to :any:`wait`:

.. code-block:: python

   @lc.computed
   def c():
       return a.wait(reset=False) + b.wait(reset=False)

and the values of ``a`` and ``b`` are updated simultaneously in a
batch:

.. code-block:: python

   with lc.batch():
       a.value = delayed(10, delay=1)
       b.value = delayed(15, delay=2)

the following is printed to standard output:

.. code-block::

   A + B = 12
   A + B = 25

If a single call to :any:`live_cells.wait` is used:

.. code-block:: python

   @lc.watch
   def c():
       x, y = lc.wait(a, b, reset=False)
       return x + y

only the following is printed after the batch update:

.. code-block::

   A + B = 25
