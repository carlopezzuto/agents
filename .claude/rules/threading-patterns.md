# Threading and Concurrency Patterns

## Overview

Standard threading patterns for Python projects. Following these patterns ensures consistent, safe, and maintainable concurrent code.

## ConditionalLock Pattern (RECOMMENDED)

A `ConditionalLock` wraps a real lock or a no-op, letting classes optionally support thread-safety without conditional checks at every call site.

### Reference Implementation

```python
import threading
from contextlib import nullcontext

class ConditionalLock:
    """Lock that can be disabled for single-threaded use."""

    def __init__(self, enabled: bool = True):
        self._lock = threading.RLock() if enabled else nullcontext()
        self._enabled = enabled

    @property
    def is_thread_safe(self) -> bool:
        return self._enabled

    def __enter__(self):
        return self._lock.__enter__()

    def __exit__(self, *args):
        return self._lock.__exit__(*args)
```

### Before (Anti-Pattern - DO NOT USE)
```python
import threading
from contextlib import nullcontext

class MyService:
    def __init__(self, thread_safe: bool = True):
        # BAD: Verbose and error-prone
        self._lock = threading.RLock() if thread_safe else None

    def do_work(self):
        # BAD: Requires nullcontext and conditional check
        with self._lock if self._lock else nullcontext():
            self._internal_work()
```

### After (Required Pattern - USE THIS)
```python
class MyService:
    def __init__(self, thread_safe: bool = True):
        # GOOD: Clean and consistent
        self._lock = ConditionalLock(thread_safe)

    def do_work(self):
        # GOOD: No conditional check needed
        with self._lock:
            self._internal_work()
```

## Lock Types and When to Use

| Lock Type | Use Case |
|-----------|----------|
| `ConditionalLock` | Most services with optional thread-safety |
| `threading.RLock` | When recursive acquisition is needed and always enabled |
| `threading.Lock` | Simple mutual exclusion (non-reentrant) |
| `asyncio.Lock` | Async code (non-reentrant) |

## Deadlock Prevention

### Never Nest Locks Without Documentation
If a method needs to acquire multiple locks, document the acquisition order:

```python
# AIDEV-NOTE: Lock order: _cache_lock -> _data_lock (always this order)
def update_with_cache(self, data):
    with self._cache_lock:
        with self._data_lock:
            self._do_update(data)
```

### Use Consistent Lock Ordering
If Class A can call Class B, and both have locks, establish a global ordering:
1. Higher-level services acquire locks first
2. Lower-level utilities acquire locks last

### Avoid Lock Acquisition in Callbacks
```python
# BAD: Callback might already hold a lock
def register_callback(self, callback):
    with self._lock:
        self._callbacks.append(callback)
        callback()  # DANGER: callback might acquire same lock!

# GOOD: Release lock before callback
def register_callback(self, callback):
    with self._lock:
        self._callbacks.append(callback)
    callback()  # Safe: lock released
```

## Lock Usage Guidelines

1. **Minimize lock scope** - Hold locks for the shortest time possible
2. **Avoid I/O while holding locks** - Don't do network/file operations under lock
3. **Don't call unknown code under lock** - User callbacks, plugins, etc.
4. **Use context managers** - Always `with self._lock:` pattern
5. **Document lock purpose** - Use AIDEV-NOTE for non-obvious locking

## Thread-Safety Protocol

Classes supporting thread-safety should implement an `IThreadSafe` protocol:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class IThreadSafe(Protocol):
    @property
    def is_thread_safe(self) -> bool: ...

class MyService:
    def __init__(self, thread_safe: bool = True):
        self._lock = ConditionalLock(thread_safe)

    @property
    def is_thread_safe(self) -> bool:
        return self._lock.is_thread_safe
```

## Testing Thread-Safe Code

1. Test with `thread_safe=True` and `thread_safe=False`
2. Use `ThreadPoolExecutor` for concurrent test scenarios
3. Consider race condition testing with `hypothesis` library

## Async Code Guidelines

For `async` code, use `asyncio.Lock` (not reentrant):

```python
import asyncio

class AsyncService:
    def __init__(self):
        self._lock = asyncio.Lock()

    async def do_work(self):
        async with self._lock:
            await self._async_operation()
```

**Note:** `asyncio.Lock` is NOT reentrant. Acquiring it twice from the same coroutine will deadlock.

## Migration Checklist

When updating existing code to use ConditionalLock:

- [ ] Replace `threading.RLock() if X else None` with `ConditionalLock(X)`
- [ ] Replace `with self._lock if self._lock else nullcontext():` with `with self._lock:`
- [ ] Remove `from contextlib import nullcontext` if no longer needed
- [ ] Verify tests pass with both thread-safe and non-thread-safe modes
