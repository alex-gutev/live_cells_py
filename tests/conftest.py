import pytest, async_solipsism

from live_cells import watch

@pytest.fixture()
def test_watch():
    """Provides a `watch` decorator that automatically stops the watch functions after the test."""

    watchers = []

    def decorator(fn=None, *args, **kwargs):
        if fn is None:
            return lambda f: decorator(f, *args, **kwargs)

        watcher = watch(fn, *args, **kwargs)
        watchers.append(watcher)

        return watcher

    yield decorator

    for watcher in watchers:
        watcher.stop()

@pytest.fixture
def event_loop_policy():
    return async_solipsism.EventLoopPolicy()
