import asyncio
import pytest

from asyncio import Future

from live_cells import (
    value,
    mutable,
    computed,
    awaited,
    batch,
    PendingAsyncValueError
)

from util import (
    observe,
    ValueTestObserver,
    MockException,
    future_value,
    future_error,
    delayed,
    is_pending
)

@pytest.mark.asyncio
class TestAwaitCell:
    """Tests the behaviour of ``awaited()`` cells."""

    async def test_constant_cell(self):
        """Test a simple coroutine held in a constant cell."""

        cell = value(future_value(12)).awaited()

        with observe(cell, ValueTestObserver()) as observer:
            await asyncio.sleep(1)

            assert cell.value == 12
            assert observer.values == [12]

    async def test_mutable_cell(self):
        """Test a simple coroutine held in a mutable cell."""

        m = mutable(future_value(12))
        c = m.awaited()

        with observe(c, ValueTestObserver()) as observer:
            await asyncio.sleep(1)
            assert c.value == 12

            m.value = future_value(100)

            is_pending(c)

            await asyncio.sleep(1)
            assert c.value == 100

            assert observer.values == [12, 100]

    async def test_notifies_observers(self):
        """Test that the observers of the cell are notified correctly."""

        m = mutable(future_value(12))
        c = m.awaited()

        with observe(c, ValueTestObserver()) as observer:
            m.value = future_value(100)
            m.value = future_value(20)
            m.value = future_value(30)

            await asyncio.sleep(1)

            assert observer.values == [30]

    async def test_computed_cell(self):
        """Test awaited on a computed cell that returns a coroutine."""

        a = mutable(future_value(1))
        b = mutable(future_value(2))

        @computed
        async def sum():
            x, y = await asyncio.gather(a(), b())
            return x + y

        cell = sum.awaited()

        with observe(cell, ValueTestObserver()) as observer:
            await asyncio.sleep(1)
            assert cell.value == 3

            a.value = future_value(5)

            is_pending(cell)

            await asyncio.sleep(1)
            assert cell.value == 7

            b.value = future_value(10)

            is_pending(cell)

            await asyncio.sleep(1)
            assert cell.value == 15

            with batch():
                a.value = future_value(20)
                b.value = future_value(30)

            is_pending(cell)

            await asyncio.sleep(1)
            assert cell.value == 50

            assert observer.values == [3, 7, 15, 50]

    async def test_delayed_computed_cell(self):
        """Test awaited() on computed cell with varying delays."""

        a = mutable(future_value(1))
        b = mutable(future_value(2))

        @computed
        async def sum():
            x, y = await asyncio.gather(a(), b())
            return x + y

        cell = sum.awaited()

        with observe(cell, ValueTestObserver()) as observer:
            await asyncio.sleep(1)
            assert cell.value == 3

            with batch():
                a.value = future_value(20)
                b.value = delayed(10, 30)

            is_pending(cell)

            await asyncio.sleep(5)
            is_pending(cell)

            await asyncio.sleep(6)

            assert cell.value == 50
            assert observer.values == [3, 50]

    async def test_latest_value(self):
        """Test that only the latest coroutine is awaited even with varying delays."""

        f = mutable(delayed(10, 1))
        w = f.awaited()

        with observe(w, ValueTestObserver()) as observer:
            f.value = future_value(2)
            f.value = delayed(30, 3)
            f.value = future_value(4)

            is_pending(w)
            assert observer.values == []

            await asyncio.sleep(5)
            assert w.value == 4
            assert observer.values == [4]

            await asyncio.sleep(6)
            assert w.value == 4
            assert observer.values == [4]

            await asyncio.sleep(10)
            assert w.value == 4
            assert observer.values == [4]

            await asyncio.sleep(30)
            assert w.value == 4
            assert observer.values == [4]

            f.value = future_value(100)
            await asyncio.sleep(1)

            assert w.value == 100
            assert observer.values == [4, 100]

    async def test_exceptions(self):
        """Test that exceptions raised in coroutines are raised by awaited() cells."""

        f = mutable(future_value(1))
        w = f.awaited()

        with observe(w, ValueTestObserver()) as observer:
            await asyncio.sleep(1)

            f.value = future_error(MockException())
            await asyncio.sleep(1)

            with pytest.raises(MockException):
                w.value

            f.value = future_value(10)
            await asyncio.sleep(1)

            assert observer.values == [1, 10]

    def test_compares_eq_same_cells(self):
        """Test that cells compare equal when give the same argument cell."""

        f = mutable(future_value(1))

        w1 = f.awaited()
        w2 = f.awaited()

        assert w1 == w2
        assert hash(w1) == hash(w2)

    def test_compares_neq_difference_cells(self):
        """Test that cells compare not equal when give different argument cells."""

        f1 = mutable(future_value(1))
        f2 = mutable(future_value(1))

        w1 = f1.awaited()
        w2 = f2.awaited()

        assert w1 != w2
        assert w1 == w1


@pytest.mark.asyncio
class TestMultiAwaitCell:
    """Test the behaviour of ``awaited()`` with multiple arguments."""

    async def test_constant_cells(self):
        """Test simple coroutines held in constant cells."""

        a = value(future_value(1))
        b = value(future_value(2))

        @computed
        def sum():
            x, y = awaited(a, b)()
            return x + y

        with observe(sum, ValueTestObserver()) as observer:
            await asyncio.sleep(1)
            assert sum.value == 3

    async def test_mutable_cells(self):
        """Test simple coroutines held in mutable cells."""

        a = mutable(future_value(1))
        b = mutable(future_value(2))

        @computed
        def sum():
            x, y = awaited(a, b)()
            return x + y

        with observe(sum, ValueTestObserver()) as observer:
            await asyncio.sleep(1)
            assert sum.value == 3

            a.value = future_value(5)
            is_pending(sum)

            await asyncio.sleep(1)
            assert sum.value == 7

            b.value = future_value(10)
            is_pending(sum)

            await asyncio.sleep(1)
            assert sum.value == 15

            with batch():
                a.value = future_value(20)
                b.value = future_value(30)

            is_pending(sum)

            await asyncio.sleep(1)
            assert sum.value == 50

            assert observer.values == [3, 7, 15, 50]

    async def test_notifies_observers(self):
        """Test that the observers of the cell are notified correctly."""

        a = mutable(future_value(1))
        b = mutable(future_value(2))

        @computed
        def sum():
            x, y = awaited(a, b)()
            return x + y

        with observe(sum, ValueTestObserver()) as observer:
            a.value = future_value(15)
            b.value = future_value(20)

            with batch():
                a.value = future_value(100)
                b.value = future_value(320)

            await asyncio.sleep(1)
            assert observer.values == [420]

    async def test_delays(self):
        """Test that coroutines with delays are handled correctly."""

        a = mutable(future_value(1))
        b = mutable(future_value(2))

        @computed
        def sum():
            x, y = awaited(a, b)()
            return x + y

        with observe(sum, ValueTestObserver()) as observer:
            await asyncio.sleep(1)
            assert sum.value == 3

            with batch():
                a.value = future_value(20)
                b.value = delayed(10, 30)

            is_pending(sum)

            await asyncio.sleep(5)
            is_pending(sum)

            await asyncio.sleep(6)
            assert sum.value == 50

            assert observer.values == [3, 50]

    async def test_latest_value(self):
        """Test that only the latest coroutine is awaited even with varying delays."""

        a = mutable(delayed(10, 1))
        b = mutable(future_value(2))

        @computed
        def w():
            x, y = awaited(a, b)()
            return x + y

        with observe(w, ValueTestObserver()) as observer:
            a.value = future_value(10)

            with batch():
                a.value = delayed(30, 20)
                b.value = future_value(7)

            a.value = future_value(100)

            is_pending(w)
            assert observer.values == []

            await asyncio.sleep(5)
            assert w.value == 107
            assert observer.values == [107]

            await asyncio.sleep(6)
            assert w.value == 107
            assert observer.values == [107]

            await asyncio.sleep(10)
            assert w.value == 107
            assert observer.values == [107]

            await asyncio.sleep(10)
            assert w.value == 107
            assert observer.values == [107]

            a.value = future_value(1000)
            await asyncio.sleep(1)
            assert w.value == 1007
            assert observer.values == [107, 1007]

    async def test_exceptions(self):
        """Test that exceptions raised in coroutines are raised by awaited() cells."""

        a = mutable(future_value(1))
        b = mutable(future_value(2))
        w = awaited(a, b)

        with observe(w, ValueTestObserver()) as observer:
            await asyncio.sleep(1)

            a.value = future_error(MockException())
            await asyncio.sleep(1)

            with pytest.raises(MockException):
                w.value

            a.value = future_value(10)
            b.value = future_error(MockException)
            await asyncio.sleep(1)

            with pytest.raises(MockException):
                w.value

            b.value = future_value(15)
            await asyncio.sleep(1)

            assert observer.values == [[1, 2], [10, 15]]

    def test_compares_eq_same_cells(self):
        """Test that cells compare equal when give the same argument cell."""

        f1 = mutable(future_value(1))
        f2 = mutable(future_value(3))

        w1 = awaited(f1, f2)
        w2 = awaited(f1, f2)

        assert w1 == w2
        assert hash(w1) == hash(w2)

    def test_compares_neq_difference_cells(self):
        """Test that cells compare not equal when give different argument cells."""

        f1 = mutable(future_value(1))
        f2 = mutable(future_value(3))
        f3 = mutable(future_value(5))

        w1 = awaited(f1, f2)
        w2 = awaited(f1, f3)
        w3 = awaited(f3, f2)

        assert w1 == w1
        assert w1 != w2
        assert w1 != w3
        assert w2 != w3
