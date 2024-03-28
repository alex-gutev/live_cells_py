import pytest

from live_cells import watch

@pytest.fixture()
def test_watch():
    """Provides a `watch` decorator that automatically stops the watch functions after the test."""

    watchers = []

    def decorator(fn):
        watcher = watch(fn)
        watchers.append(watcher)

        return watcher

    yield decorator

    for watcher in watchers:
        watcher.stop()
