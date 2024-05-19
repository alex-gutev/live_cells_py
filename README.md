# Live Cells Python

> [!CAUTION]
> This software is still in beta, and will likely experience rapid
> changes before the first official release.

Live Cells Python is a reactive programming library for Python, ported
from [Live Cells](https://livecells.viditrack.com/) for Dart.

## Examples

> [!NOTE]
> This section contains examples demonstrating the main features of
> the library. Head to the
> [documentation](https://alex-gutev.github.io/live_cells_py/index.html),
> for more information on how to use this library.

The basic building block of Live Cells is the cell, which is an object
with a value and a set of observers, which react to changes in the
value.

Cells are defined as follows:

```python
import live_cells as lc

a = lc.mutable(0);
a = lc.mutable(0);
```

And are observed as follows:

```python
lc.watch(lambda: print(f'{a()}, {b()}'))
```

The *watch function* defined above prints the values of the cells `a`
and `b` to standard output. It is called whenever the value of `a` or
`b` changes.

For example the following code, which sets the values of `a` and `b`:

```python
a.value = 1;
b.value = 2;
a.value = 3;
```

Results in the following being printed to standard output:

```
1, 0
1, 2
3, 2
```

Watch functions comprising multiple statements can be defined using
the decorator of `watch`:

```python
@lc.watch
def watcher():
	print(f'A = {a()}')
	print(f'B = {b()}')
```

Cells can also be defined as a function of the values of one or more
cells. For example the following cell is defined as the sum of cells
`a` and `b`:

```python
c = lc.computed(lambda: a() + b())
```

The value of cell `c` is recomputed automatically whenever the value
of either `a` or `b` changes.

This cell can also be defined more succinctly as an expression of cells:

```python
c = a + b;
```

When the following is executed:

```python
a.value = 90
b.value = 30
```

The following message is printed to standard output automatically:

```
Sum exceeds 100!!!
```
