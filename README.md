Command line tool for rerunning a command when file dependencies change.

## Example usage
- `pwatch pytest` will automatically run your pytest tests as source files are saved.
- `pwatch -c 'make && ./a.out'` will build and run an executable as you save source files.

## Description
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
pwatch is current Linux-only (macOS may be supported in the future). pwatch also requires Python 3.6+.

## Comparison to Alternatives
`inotifywait` can provide similar functionality to `pwatch`. However, with `inotifywait` files need to be explicitly specified while they are automatically detected with `pwatch`. Explicitly specifying files can be cumbersome and if you watch a directory, then a rerun may be retriggered unvoluntairly if your text editor creates temporary backup files in the source tree. In summary, `pwatch` provides a simpler interface that 'just works'.

## Development Setup
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
