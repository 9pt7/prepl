Command line tool for rerunning a command when file dependencies change.

## Example usage
- `pwatch pytest` will automatically run your pytest tests as source files are saved.
- `pwatch -c 'make && ./a.out'` will build and run an executable as you save source files.

## Description
pwatch monitors files that were accessed by the command process and reruns it when any of the files change. pwatch can be run  with either a single command or with a command string that is executed in a shell. The second form is useful when you want to run multiple commands (like build a project, then run some tests).
```
usage: pwatch [-h] [-c COMMAND_STRING] ...

Autorun command on file change.

positional arguments:
  COMMAND ...        the command to run and any arguments

optional arguments:
  -h, --help         show this help message and exit
  -c COMMAND_STRING  command string to run in shell (alternative to COMMAND ...)
```

## Installation
pwatch current supports Linux. macOS may be supported in the future. pwatch requires Python 3.6+.

## Motivation
While developing software and writing tests it is typically advantageous to immediately see the result of code changes while they are being made. Some testing frameworks like jest rerun tests when source files are changed but they are limited to the languages that the testing framework supports. Other tools like inotifywait, fswatch, entr, etc. provide a generic interface for rerunning a command when files change, but these tools require the files to monitor to be explicitly specified. This can be cumbersome because in addition to specifying all the files to monitor, it is also typically necessary to exclude build directories and temporary backup files created by editors, for instance, that may inadventantly trigger the command to be rerun. pwatch provides its functionality for any programming language without requiring an explitcit list to files to monitor.

## Example Development Setup
```
# Note: the repository's submodules must be cloned
git clone --recurse-submodules git@github.com:9pt7/pwatch.git

# Setup a virtual environment...
python3 -m venv pwatch
cd pwatch
source ./bin/activate

# Install the package in editable mode with development dependencies
pip3 install --editable .[dev]

# Run tests
pytest pwatch

# Test packaging with tox
tox
```
