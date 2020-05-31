Command line tool for rerunning a command when file dependencies change.

## Example usage
- `pwatch pytest` will automatically run your pytest tests as source files are saved.
- `pwatch -c 'make && ./a.out'` will build and run an executable as you save source files.

## Description
```
usage: pwatch [-h] [-c COMMAND_STRING] [--debug] ...

Autorun command on file change.

positional arguments:
  command            the command to run

optional arguments:
  -h, --help         show this help message and exit
  -c COMMAND_STRING  string to run in shell
  --debug            use debug-level logging
```

## Installation
TODO

## Comparison to Alternatives
`inotifywait` can provide similar functionality to `pwatch`. However, with `inotifywait` files need to be explicitly specified while they are automatically detected with `pwatch`. Explicitly specifying files can be cumbersome and if you watch a directory, then a rerun may be retriggered unvoluntairly if your text editor creates temporary backup files in the source tree. In summary, `pwatch` provides a simpler interface that 'just works'.

## How it works
When `COMMAND` is executed, `pwatch` loads a shared library into the running process via the `LD_PRELOAD` environment variable. The shared library intercepts calls to `libc` that access the filesystem so `pwatch` can build a list of files to observe. `COMMAND` is executed each time any file being observed is changed.
