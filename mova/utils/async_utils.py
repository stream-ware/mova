"""
⚡ Async Utilities - Advanced Asynchronous Programming Utilities

Comprehensive async utilities for concurrent programming, task management,
timeout handling, retry mechanisms, and performance optimization.
"""

import asyncio
import functools
import time
from typing import Any, Awaitable, Callable, List, Optional, TypeVar, Union, Dict
from contextlib import asynccontextmanager
import logging


T = TypeVar('T')


async def run_async(func: Callable, *args, **kwargs) -> Any:
    """
    Run synchronous function in async context

    Args:
        func: Synchronous function to run
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result
    """
    try:
        loop = asyncio.get_event_loop()

        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run in thread pool for CPU-bound tasks
            return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

    except Exception as e:
        logging.error(f"Error running async function: {e}")
        raise


async def gather_with_concurrency(limit: int, *awaitables: Awaitable[T]) -> List[T]:
    """
    Run awaitables with concurrency limit

    Args:
        limit: Maximum concurrent tasks
        *awaitables: Awaitable objects to execute

    Returns:
        List of results in original order
    """
    try:
        semaphore = asyncio.Semaphore(limit)

        async def _limited_task(awaitable: Awaitable[T]) -> T:
            async with semaphore:
                return await awaitable

        # Wrap all awaitables with semaphore
        limited_tasks = [_limited_task(aw) for aw in awaitables]

        return await asyncio.gather(*limited_tasks)

    except Exception as e:
        logging.error(f"Error in concurrent execution: {e}")
        raise


async def timeout_after(seconds: float, coro: Awaitable[T],
                       default: Optional[T] = None) -> Optional[T]:
    """
    Execute coroutine with timeout

    Args:
        seconds: Timeout in seconds
        coro: Coroutine to execute
        default: Default value on timeout

    Returns:
        Coroutine result or default on timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        logging.warning(f"Coroutine timed out after {seconds}s")
        return default
    except Exception as e:
        logging.error(f"Error in timeout execution: {e}")
        raise


def async_retry(max_attempts: int = 3, delay: float = 1.0,
               backoff_factor: float = 2.0,
               exceptions: tuple = (Exception,)) -> Callable:
    """
    Async retry decorator

    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated async function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        raise e

                    logging.warning(f"Attempt {attempt} failed for {func.__name__}: {e}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor

            return None  # Should never reach here

        return wrapper
    return decorator


class TaskGroup:
    """
    Task group for managing multiple async tasks
    """

    def __init__(self, name: str = "TaskGroup"):
        """
        Initialize TaskGroup

        Args:
            name: Name for the task group
        """
        self.name = name
        self.tasks: List[asyncio.Task] = []
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, Exception] = {}
        self.logger = logging.getLogger(__name__)

    def add_task(self, coro: Awaitable[T], name: Optional[str] = None) -> asyncio.Task:
        """
        Add task to group

        Args:
            coro: Coroutine to add
            name: Optional task name

        Returns:
            Created task
        """
        try:
            task = asyncio.create_task(coro)
            if name:
                task.set_name(name)

            self.tasks.append(task)
            self.logger.debug(f"Added task '{name or 'unnamed'}' to group '{self.name}'")

            return task

        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            raise

    async def wait_all(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Wait for all tasks to complete

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Dictionary of task results
        """
        try:
            if not self.tasks:
                return {}

            # Wait for all tasks
            if timeout:
                done, pending = await asyncio.wait(
                    self.tasks,
                    timeout=timeout,
                    return_when=asyncio.ALL_COMPLETED
                )

                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            else:
                done, _ = await asyncio.wait(
                    self.tasks,
                    return_when=asyncio.ALL_COMPLETED
                )

            # Collect results and errors
            for task in done:
                task_name = task.get_name()

                try:
                    result = task.result()
                    self.results[task_name] = result
                except Exception as e:
                    self.errors[task_name] = e
                    self.logger.error(f"Task '{task_name}' failed: {e}")

            self.logger.info(f"Task group '{self.name}' completed: "
                           f"{len(self.results)} successful, {len(self.errors)} failed")

            return self.results

        except Exception as e:
            self.logger.error(f"Error waiting for tasks: {e}")
            raise

    async def wait_first(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Wait for first task to complete

        Args:
            timeout: Optional timeout in seconds

        Returns:
            First task result or None
        """
        try:
            if not self.tasks:
                return None

            done, pending = await asyncio.wait(
                self.tasks,
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED
            )

            if not done:
                return None

            # Get first completed task
            first_task = next(iter(done))
            task_name = first_task.get_name()

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            try:
                result = first_task.result()
                self.logger.info(f"First task '{task_name}' completed successfully")
                return result
            except Exception as e:
                self.logger.error(f"First task '{task_name}' failed: {e}")
                raise

        except Exception as e:
            self.logger.error(f"Error waiting for first task: {e}")
            raise

    def cancel_all(self) -> int:
        """
        Cancel all tasks in group

        Returns:
            Number of tasks cancelled
        """
        try:
            cancelled_count = 0

            for task in self.tasks:
                if not task.done():
                    task.cancel()
                    cancelled_count += 1

            self.logger.info(f"Cancelled {cancelled_count} tasks in group '{self.name}'")
            return cancelled_count

        except Exception as e:
            self.logger.error(f"Error cancelling tasks: {e}")
            return 0

    def get_status(self) -> Dict[str, int]:
        """
        Get task group status

        Returns:
            Status dictionary with counts
        """
        try:
            status = {
                'total': len(self.tasks),
                'completed': 0,
                'running': 0,
                'cancelled': 0,
                'failed': 0
            }

            for task in self.tasks:
                if task.done():
                    if task.cancelled():
                        status['cancelled'] += 1
                    elif task.exception():
                        status['failed'] += 1
                    else:
                        status['completed'] += 1
                else:
                    status['running'] += 1

            return status

        except Exception as e:
            self.logger.error(f"Error getting task status: {e}")
            return {}


def create_task_group(name: str = "TaskGroup") -> TaskGroup:
    """
    Create new task group

    Args:
        name: Name for the task group

    Returns:
        New TaskGroup instance
    """
    return TaskGroup(name)


@asynccontextmanager
async def async_context_manager(setup_coro: Awaitable[T],
                               cleanup_coro: Optional[Awaitable] = None):
    """
    Create async context manager from coroutines

    Args:
        setup_coro: Setup coroutine
        cleanup_coro: Optional cleanup coroutine

    Yields:
        Result from setup coroutine
    """
    resource = None
    try:
        resource = await setup_coro
        yield resource
    finally:
        if cleanup_coro:
            try:
                await cleanup_coro
            except Exception as e:
                logging.error(f"Error in cleanup: {e}")


class AsyncQueue:
    """
    Enhanced async queue with additional features
    """

    def __init__(self, maxsize: int = 0):
        """
        Initialize AsyncQueue

        Args:
            maxsize: Maximum queue size (0 = unlimited)
        """
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.consumers: List[asyncio.Task] = []
        self.running = False
        self.logger = logging.getLogger(__name__)

    async def put(self, item: Any, timeout: Optional[float] = None) -> bool:
        """
        Put item in queue with timeout

        Args:
            item: Item to put
            timeout: Optional timeout

        Returns:
            True if item was put successfully
        """
        try:
            if timeout:
                await asyncio.wait_for(self.queue.put(item), timeout=timeout)
            else:
                await self.queue.put(item)
            return True
        except asyncio.TimeoutError:
            self.logger.warning("Queue put operation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error putting item in queue: {e}")
            return False

    async def get(self, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Get item from queue with timeout

        Args:
            timeout: Optional timeout

        Returns:
            Queue item or None on timeout
        """
        try:
            if timeout:
                return await asyncio.wait_for(self.queue.get(), timeout=timeout)
            else:
                return await self.queue.get()
        except asyncio.TimeoutError:
            self.logger.warning("Queue get operation timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error getting item from queue: {e}")
            return None

    def size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()

    def empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()

    def full(self) -> bool:
        """Check if queue is full"""
        return self.queue.full()


async def async_map(func: Callable, items: List[Any],
                   concurrency: int = 10) -> List[Any]:
    """
    Apply async function to list of items with concurrency control

    Args:
        func: Async function to apply
        items: List of items
        concurrency: Maximum concurrent tasks

    Returns:
        List of results
    """
    try:
        semaphore = asyncio.Semaphore(concurrency)

        async def _process_item(item):
            async with semaphore:
                return await func(item)

        tasks = [_process_item(item) for item in items]
        return await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(f"Error in async map: {e}")
        raise


def async_cached(ttl: float = 300.0) -> Callable:
    """
    Async function caching decorator with TTL

    Args:
        ttl: Time to live in seconds

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[str, tuple] = {}  # key -> (result, timestamp)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()

            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[key] = (result, current_time)

            # Clean old entries (simple cleanup)
            if len(cache) > 1000:  # Prevent unbounded growth
                cutoff_time = current_time - ttl
                cache = {k: v for k, v in cache.items() if v[1] > cutoff_time}

            return result

        return wrapper
    return decorator


async def async_sleep_with_jitter(base_delay: float, jitter_factor: float = 0.1):
    """
    Sleep with random jitter to avoid thundering herd

    Args:
        base_delay: Base delay in seconds
        jitter_factor: Jitter factor (0.0 to 1.0)
    """
    import random

    jitter = random.uniform(-jitter_factor, jitter_factor) * base_delay
    actual_delay = max(0, base_delay + jitter)

    await asyncio.sleep(actual_delay)
