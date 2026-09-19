# mova-core

`mova-core` provides local configuration, structured logging, synchronous HTTP
and WebSocket clients, and utility helpers for the Mova ecosystem.

Process execution is deliberately fail-closed: callers must pass an explicit
argv sequence and the exact executable names they permit. The package does not
provide a shell-execution server.

## Development

```bash
python -m pytest mova/tests -q
python -m build
```
