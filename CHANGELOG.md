# 0.2.0 - 2025-06-25

New features:

* `waited()` and `wait()` functions/methods for creating cells that
  observe the result of *awaitables*.

# 0.1.5 - 2024-06-24

* Fix issue with scheduled watch function:
  
  Incorrect values were being read for referenced argument cells.

# 0.1.4 - 2024-05-22

* Fix issue with unit tests being installed as `tests` package.

# 0.1.3 - 2024-05-21

* Fix bugs in examples in README

# 0.1.2 - 2024-05-21

* Fix issue with argument cell tracking on green threads.

# 0.1.1 - 2024-05-20

* Add installation instructions to README.

# 0.1.0 - 2024-05-19

Initial Release.

The following features are ported from Live Cells Dart:

* Mutable Cells
* Computed Cells
* Batch Updates
* Watch Functions
* Peek Cells
