class Maybe:
    """Wraps the result or error of a cell computation.

    A Maybe can either represent the value of a cell that was computed
    successfully, in which case ``value`` is not *None* and holds the
    value, or an exception that was raised while computing the value
    of a cell, in which case ``error`` is not *None* and holds the
    raised exception.

    :param value: The computed value or *None* if an exception was
                  raised.

    :param error: The exception raised while computing the value or
                  *None* if no exception was raised.

    """

    def __init__(self, value=None, error=None):
        self._value = value
        self._error = error

    @property
    def value(self):
        """The computed value of the cell.

        This is *None* if an exception was raised while computing the
        cell's value.

        """

        return self._value

    @property
    def error(self):
        """The exception raised while computing the value of the cell.

        This is *None* if no exception was raised while computing the
        cell's value.

        """

        return self._error

    @classmethod
    def wrap(cls, compute):
        """Wrap the result of a computation in a Maybe representing a value/error.

        ``compute`` is called to compute a value. If ``compute``
        returns a value, a Maybe representing a value is returned. If
        ``compute`` raises an exception, a Maybe representing an error
        is returned.

        :param compute: A function of no arguments.
        :type compute: function

        :returns: A Maybe representing the result returned by
                  ``compute``.

        :rtype: Maybe

        """

        try:
            return cls(value = compute())

        except Exception as e:
            return cls(error = e)

    @classmethod
    def wrap_async(cls, compute):
        """Create a coroutine that returns the result of ``compute()`` in a ``Maybe``.

        If the coroutine returned by ``compute()`` completes with a
        value, the returned ``Maybe`` holds the value.

        If the coroutine raises an exception, the returned ``Maybe``
        holds the exception.

        :param compute: A Function that should return a coroutine when
                        it is called (with no arguments).

        :returns: A coroutine that returns the result of calling
                  ``compute()`` in a ``Maybe``

        """

        async def async_maybe(coro):
            try:
                return cls(value=await coro)

            except Exception as e:
                return cls(error=e)

        try:
            return async_maybe(compute())

        except Exception as e:
            return cls(error=e)

    def unwrap(self):
        """Return the value or raise the exception held in this Maybe.

        :returns: The value held in this Maybe if it represents a
                  value.

        :raises: The exception held in this Maybe if it represents an
                 error.

        """

        if self.error is not None:
            raise self.error

        return self.value

    def __eq__(self, other):
        if isinstance(other, Maybe):
            return value == other.value and error == other.error

        return NotImplemented

    def __hash__(self):
        return hash((value, error))

    def __repr__(self):
        if self.error is not None:
            return f'Maybe(error={self.error})'

        else:
            return f'Maybe(value={self.value})'
