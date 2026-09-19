# Ticket 001: recover and harden `mova-core`

Issue: https://github.com/stream-ware/mova/issues/1

This recovery imports only the coherent `mova-core` package from the local
independent history. It excludes legacy duplicate trees, voice extensions,
`grok3`, and all uncommitted files in the original checkout.

The recovered package uses synchronous `requests` consistently in its tests,
declares its `psutil` dependency, and does not create `mova.log` in the current
directory. `run_command` rejects shell strings, requires explicit argv, and
requires the caller to provide an exact executable allowlist before a process
can start. No service endpoint or real command execution is added or invoked.

Validation includes the original regression suite, the new execution-boundary
tests, a package build, and source compilation.
