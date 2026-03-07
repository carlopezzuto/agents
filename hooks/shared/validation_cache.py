#!/usr/bin/env python3
"""
Smart Caching System for Rankle Quality Validation

Provides content-hash based caching for AST analysis and toolchain results.
Designed to achieve 60-70% speedup for repeated validations.

Key features:
- Content-hash based cache keys (SHA-256)
- LRU eviction with configurable size limits
- Separate caches for AST and toolchain results
- Thread-safe operations
- Memory-efficient storage
"""

import hashlib
import json
import sys
import threading
import time
from collections import OrderedDict
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class CacheType(Enum):
    """Types of cached validation results."""

    AST_ANALYSIS = "ast_analysis"
    CLEAN_CODE = "clean_code"
    TOOLCHAIN = "toolchain"
    COMBINED = "combined"


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""

    data: Any
    timestamp: float
    access_count: int
    content_hash: str
    file_path: str
    cache_type: CacheType

    def touch(self):
        """Update access timestamp and increment count."""
        self.timestamp = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    memory_usage_bytes: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        return (
            (self.cache_hits / self.total_requests * 100)
            if self.total_requests > 0
            else 0.0
        )


class LRUCache:
    """
    Thread-safe LRU cache with size limits and eviction strategies.

    Optimized for high-performance validation caching with automatic cleanup.
    """

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 50):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()

    def get(self, cache_key: str) -> Any | None:
        """
        Get cached data by key.

        Args:
            cache_key: Content hash key

        Returns:
            Cached data if found, None otherwise
        """
        with self._lock:
            self._stats.total_requests += 1

            if cache_key in self._cache:
                # Move to end (most recently used)
                entry = self._cache.pop(cache_key)
                entry.touch()
                self._cache[cache_key] = entry

                self._stats.cache_hits += 1
                return entry.data

            self._stats.cache_misses += 1
            return None

    def put(
        self,
        cache_key: str,
        data: Any,
        content_hash: str,
        file_path: str,
        cache_type: CacheType,
    ):
        """
        Store data in cache with LRU eviction.

        Args:
            cache_key: Content hash key
            data: Data to cache
            content_hash: SHA-256 hash of content
            file_path: Source file path
            cache_type: Type of cached data
        """
        with self._lock:
            # Remove existing entry if present
            if cache_key in self._cache:
                del self._cache[cache_key]

            # Create new entry
            entry = CacheEntry(
                data=data,
                timestamp=time.time(),
                access_count=1,
                content_hash=content_hash,
                file_path=file_path,
                cache_type=cache_type,
            )

            # Add to cache
            self._cache[cache_key] = entry

            # Perform eviction if necessary
            self._evict_if_needed()

    def _evict_if_needed(self):
        """Evict entries if cache exceeds size or memory limits."""
        # Evict by size
        while len(self._cache) > self.max_size:
            self._evict_oldest()

        # Evict by memory usage (approximate)
        while self._estimate_memory_usage() > self.max_memory_bytes:
            self._evict_oldest()

    def _evict_oldest(self):
        """Remove the least recently used entry."""
        if self._cache:
            self._cache.popitem(last=False)
            self._stats.evictions += 1

    def _estimate_memory_usage(self) -> int:
        """Estimate total memory usage of cache entries."""
        if not self._cache:
            return 0

        # Simple estimation based on JSON serialization size
        try:
            sample_size = 0
            sample_count = min(10, len(self._cache))

            for entry in list(self._cache.values())[:sample_count]:
                sample_size += len(
                    json.dumps(asdict(entry), default=str).encode("utf-8")
                )

            # Extrapolate to full cache
            if sample_count > 0:
                avg_entry_size = sample_size / sample_count
                total_size = int(avg_entry_size * len(self._cache))
                self._stats.memory_usage_bytes = total_size
                return total_size

        except Exception:
            # Fallback estimation
            pass

        # Conservative fallback
        estimated_size = len(self._cache) * 1024  # 1KB per entry estimate
        self._stats.memory_usage_bytes = estimated_size
        return estimated_size

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()

    def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        with self._lock:
            self._estimate_memory_usage()  # Update memory stats
            return self._stats

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


class ValidationCache:
    """
    Smart caching system for Rankle quality validation.

    Provides high-performance caching with content-hash based keys
    and intelligent eviction strategies.
    """

    def __init__(self, max_size: int = 500, max_memory_mb: int = 25):
        """
        Initialize validation cache.

        Args:
            max_size: Maximum cache entries
            max_memory_mb: Maximum memory usage in MB
        """
        self._cache = LRUCache(max_size, max_memory_mb)
        self._enabled = True

    def _compute_content_hash(self, content: str) -> str:
        """
        Compute SHA-256 hash of content for cache key.

        Args:
            content: File content to hash

        Returns:
            Hexadecimal SHA-256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _make_cache_key(self, content_hash: str, cache_type: CacheType) -> str:
        """
        Create cache key combining content hash and validation type.

        Args:
            content_hash: SHA-256 hash of content
            cache_type: Type of cached validation

        Returns:
            Unique cache key
        """
        return f"{cache_type.value}:{content_hash}"

    def get_clean_code_violations(
        self, content: str, file_path: str
    ) -> list[Any] | None:
        """
        Get cached Clean Code validation results.

        Args:
            content: File content
            file_path: Source file path

        Returns:
            Cached violations list or None if not found
        """
        if not self._enabled:
            return None

        content_hash = self._compute_content_hash(content)
        cache_key = self._make_cache_key(content_hash, CacheType.CLEAN_CODE)

        return self._cache.get(cache_key)

    def cache_clean_code_violations(
        self, content: str, file_path: str, violations: list[Any]
    ):
        """
        Cache Clean Code validation results.

        Args:
            content: File content
            file_path: Source file path
            violations: Validation violations to cache
        """
        if not self._enabled:
            return

        content_hash = self._compute_content_hash(content)
        cache_key = self._make_cache_key(content_hash, CacheType.CLEAN_CODE)

        self._cache.put(
            cache_key, violations, content_hash, file_path, CacheType.CLEAN_CODE
        )

    def get_toolchain_violations(
        self, content: str, file_path: str
    ) -> list[Any] | None:
        """
        Get cached toolchain validation results.

        Args:
            content: File content
            file_path: Source file path

        Returns:
            Cached violations list or None if not found
        """
        if not self._enabled:
            return None

        content_hash = self._compute_content_hash(content)
        cache_key = self._make_cache_key(content_hash, CacheType.TOOLCHAIN)

        return self._cache.get(cache_key)

    def cache_toolchain_violations(
        self, content: str, file_path: str, violations: list[Any]
    ):
        """
        Cache toolchain validation results.

        Args:
            content: File content
            file_path: Source file path
            violations: Toolchain violations to cache
        """
        if not self._enabled:
            return

        content_hash = self._compute_content_hash(content)
        cache_key = self._make_cache_key(content_hash, CacheType.TOOLCHAIN)

        self._cache.put(
            cache_key, violations, content_hash, file_path, CacheType.TOOLCHAIN
        )

    def get_combined_result(
        self, content: str, file_path: str
    ) -> tuple[list[Any], list[Any]] | None:
        """
        Get cached combined validation result (Clean Code + Toolchain).

        Args:
            content: File content
            file_path: Source file path

        Returns:
            Tuple of (clean_violations, toolchain_violations) or None
        """
        if not self._enabled:
            return None

        content_hash = self._compute_content_hash(content)
        cache_key = self._make_cache_key(content_hash, CacheType.COMBINED)

        return self._cache.get(cache_key)

    def cache_combined_result(
        self,
        content: str,
        file_path: str,
        clean_violations: list[Any],
        toolchain_violations: list[Any],
    ):
        """
        Cache combined validation result.

        Args:
            content: File content
            file_path: Source file path
            clean_violations: Clean Code violations
            toolchain_violations: Toolchain violations
        """
        if not self._enabled:
            return

        content_hash = self._compute_content_hash(content)
        cache_key = self._make_cache_key(content_hash, CacheType.COMBINED)

        combined_result = (clean_violations, toolchain_violations)
        self._cache.put(
            cache_key, combined_result, content_hash, file_path, CacheType.COMBINED
        )

    def clear(self):
        """Clear all cached validation results."""
        self._cache.clear()

    def enable(self):
        """Enable caching."""
        self._enabled = True

    def disable(self):
        """Disable caching (for testing or debugging)."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._enabled

    def get_stats(self) -> dict[str, Any]:
        """
        Get comprehensive cache statistics.

        Returns:
            Dictionary with cache performance metrics
        """
        cache_stats = self._cache.get_stats()

        return {
            "enabled": self._enabled,
            "total_requests": cache_stats.total_requests,
            "cache_hits": cache_stats.cache_hits,
            "cache_misses": cache_stats.cache_misses,
            "hit_rate_percent": round(cache_stats.hit_rate, 2),
            "evictions": cache_stats.evictions,
            "current_size": self._cache.size(),
            "max_size": self._cache.max_size,
            "memory_usage_kb": round(cache_stats.memory_usage_bytes / 1024, 2),
            "max_memory_mb": round(self._cache.max_memory_bytes / (1024 * 1024), 2),
        }

    def get_performance_summary(self) -> str:
        """
        Get human-readable performance summary.

        Returns:
            Formatted string with key performance metrics
        """
        stats = self.get_stats()

        return f"""Validation Cache Performance:
  Hit Rate: {stats['hit_rate_percent']:.1f}% ({stats['cache_hits']}/{stats['total_requests']} requests)
  Cache Size: {stats['current_size']}/{stats['max_size']} entries
  Memory Usage: {stats['memory_usage_kb']:.1f}KB/{stats['max_memory_mb']}MB
  Evictions: {stats['evictions']}
  Status: {'Enabled' if stats['enabled'] else 'Disabled'}"""


# AIDEV-NOTE: Global cache instance for shared use
_global_cache = None
_cache_lock = threading.Lock()


def get_validation_cache() -> ValidationCache:
    """
    Get global validation cache instance (singleton pattern).

    Returns:
        Shared ValidationCache instance
    """
    global _global_cache

    if _global_cache is None:
        with _cache_lock:
            if _global_cache is None:
                _global_cache = ValidationCache()

    return _global_cache


def clear_global_cache():
    """Clear the global validation cache."""
    cache = get_validation_cache()
    cache.clear()


if __name__ == "__main__":
    # Simple test of the caching system
    cache = ValidationCache(max_size=10, max_memory_mb=1)

    # Test data
    test_content = "def test(): pass"
    test_violations = ["Test violation"]

    print("Testing validation cache...", file=sys.stderr)

    # Test cache miss
    result = cache.get_clean_code_violations(test_content, "test.py")
    print(f"Cache miss result: {result}", file=sys.stderr)

    # Test cache store
    cache.cache_clean_code_violations(test_content, "test.py", test_violations)

    # Test cache hit
    result = cache.get_clean_code_violations(test_content, "test.py")
    print(f"Cache hit result: {result}", file=sys.stderr)

    # Print stats
    print("\n" + cache.get_performance_summary(), file=sys.stderr)
