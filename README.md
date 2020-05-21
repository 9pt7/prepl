## Usage
```
usage: pwatch [-h] command [args ...]

Autorun command on file change.

positional arguments:
  command     the command to run
  args        additional arguments for command

optional arguments:
  -h, --help  show this help message and exit
```

## Installation
TODO

## Comparison to Alternatives
`inotifywait` can provide similar functionality to `pwatch`. However, with `inotifywait` files need to be explicitly specified while they are automatically detected with `pwatch`. Explicitly specifying files can be cumbersome and if you watch a directory, then a rerun may be retriggered unvoluntairly if your text editor creates temporary backup files in the source tree. In summary, `pwatch` provides a simpler interface that 'just works'.

## How it works
When `COMMAND` is executed, `pwatch` loads a shared library into the running process via the `LD_PRELOAD` environment variable. The shared library intercepts calls to `libc` that access the filesystem so `pwatch` can build a list of files to observe. `COMMAND` is executed each time any file being observed is changed.

## Contribution Guidelines
TODO
