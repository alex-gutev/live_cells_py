Pitfalls
========

This page documents some common pitfalls when using Live Cells. Please
go through this page carefully before using this library.

=========
Threading
=========

Cells are not thread safe and their values should only be read and
changed from a single thread. All interactions with cells should be
designated to a single thread, which serves as the "main" thread.

Care needs to be taken when using Live Cells with *green threading*
libraries such as `gevent <https://www.gevent.org/>`_ and `eventlet
<https://eventlet.readthedocs.io>`_. *Green threads* are lightweight
threads, with multiple green threads running on a single OS thread. In
general green threading libraries work by *monkey-patching* functions
that perform blocking IO and replacing them with asynchronous
variants. When a "blocking" function is called in a green thread, the
thread yields execution to another green thread until the blocking
operation completes.

It is safe to read and even change the values of cells from multiple
green threads, provided the green threads run on a single OS
thread. However, the process of updating the values of cells should
not be interrupted. To avoid this you should adhere to the following rules:

* **Do not** call blocking IO functions within computed cells.
* **Do not** call blocking IO functions in a context managed by :any:`live_cells.batch`.
* Blocking IO functions may only be called within watch functions
  that are scheduled to run on a new green thread.

Regarding the last point, if you must call a blocking IO function
inside a watch function, you should provide a ``schedule`` function
that creates a new green thread on which the watch function is
run. For example, if you're using *gevent* provide ``gevent.spawn`` as
the ``schedule`` function. Here's an example:

.. code-block:: python

   import gevent
   import live_cells as lc

   a = lc.mutable(0)

   @lc.watch(schedule=gevent.spawn)
   def watch_a():
       print(f'A = {a()}')
       log_to_file(a())

   a.value = 2
   a.value = 10

There is no danger of missed updates because the watch function sees
the values of the referenced cells, ``a`` in this case, as they are at
the time the watch function is scheduled and not at the time the watch
function is run. In this example, the following is printed to standard
output:

.. code-block:: text

   A = 0
   A = 2
   A = 10

Even though the value of ``a`` is changed to ``10`` immediately after
it is set to ``2`` before the watch function has been run.
