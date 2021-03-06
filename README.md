# prepl

A flexible command line tool for rerunning a command when file dependencies change.

## Example usage
- `prepl pytest` will automatically run your pytest tests as source files are saved.
- `prepl -c 'make && ./a.out'` will build and run an executable as you save source files.

## Description
The primary use case for prepl is to automatically test your code when source files are saved. This is particularly useful in test-driven development where code is continuously tested during the development process in short iterations.

prepl can be used with virtually any programming language; you just need to provide it with a command to run. prepl monitors the files that were accessed by the supplied command and reruns it when any of the files are updated.

prepl can be run with either a single command or with a command string that is executed in a shell. The second form is useful when you want to run multiple commands (like build the project, then run the tests).
```
usage: prepl [-h] [-c COMMAND_STRING] ...

Autorun command on file change.

positional arguments:
  COMMAND ...        the command to run and any arguments

optional arguments:
  -h, --help         show this help message and exit
  -c COMMAND_STRING  command string to run in shell (alternative to COMMAND ...)
```

## Installation
prepl current supports Linux. macOS may be supported in the future. prepl requires Python 3.6+.

You can install the latest release with
```
pip3 install prepl
```

## Motivation
Some testing frameworks like jest rerun tests when source files are changed but they are limited to the languages that the testing framework supports. Other tools like inotifywait, fswatch, entr, etc. provide a generic interface for rerunning a command when files change, but these tools require the files to monitor to be explicitly specified. This can be cumbersome because in addition to specifying all the files to monitor, it is also typically necessary to exclude build directories and temporary backup files created by editors, for instance, that may inadvertently trigger the command to be rerun. prepl provides its functionality for any programming language without requiring an explicit list of files to monitor.

## Example Development Setup
```
# Note: the repository's submodules must be cloned
git clone --recurse-submodules git@github.com:9pt7/prepl.git

# Setup a virtual environment...
python3 -m venv prepl
cd prepl
source ./bin/activate

# Install the package in editable mode with development dependencies
pip3 install --editable .[dev]

# Run tests
pytest prepl

# Test packaging with tox
tox
```
