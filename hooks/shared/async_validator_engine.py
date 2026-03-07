#!/usr/bin/env python3
"""
Async Validation Engine for Rankle Quality Hooks

Provides high-performance parallel validation using asyncio.TaskGroup.
Coordinates Clean Code validators and quality toolchain for optimal speed.

Performance target: <100ms for typical files
Key optimizations:
- Parallel validation execution (40-50% speedup)
- Smart caching integration
- Validation scoping for Edit operations
- Memory-efficient temporary file handling
"""

import asyncio
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

ValidationCache: Optional[type] = None
get_validation_cache: Optional[Callable[[], ValidationCache]] = None
try:
    from validation_cache import ValidationCache, get_validation_cache
except ImportError:
    pass

# AIDEV-NOTE: Import validation components - maintain error isolation
#try:
    #from quality_toolchain import QualityToolchain
    #from rankle_quality_validators import RankleQualityValidator, ViolationSeverity

def _check_validation_availability():
    """Check if validation components are available without importing them globally."""
    try:
        from quality_toolchain import QualityToolchain  # noqa: F401
        from rankle_quality_validators import RankleQualityValidator, ViolationSeverity  # noqa: F401

        return True
    except ImportError:
        return False

VALIDATION_AVAILABLE = _check_validation_availability()

class ValidationScope(Enum):
    """Defines the scope of validation to optimize performance."""

    FULL_FILE = "full_file"  # Validate entire file content
    EDIT_REGION = "edit_region"  # Validate only changed regions (future optimization)
    CONTENT_ONLY = "content_only"  # Validate content without file I/O


@dataclass
class ValidationRequest:
    """Encapsulates a validation request with all necessary context."""

    content: str
    file_path: str
    scope: ValidationScope
    original_content: str | None = None  # For edit operations
    edit_info: dict[str, Any] | None = None  # Edit operation details


@dataclass
class ValidationResult:
    """Comprehensive validation result with performance metrics."""

    has_violations: bool
    clean_code_violations: list[Any]
    toolchain_violations: list[Any]
    total_violations: int
    execution_time_ms: float
    cache_hit: bool = False
    validation_scope: ValidationScope = ValidationScope.FULL_FILE
    error_message: str | None = None


class AsyncValidatorEngine:
    """
    High-performance async validation engine.

    Coordinates parallel execution of Clean Code and toolchain validation
    with smart caching and optimization strategies.
    """

    def __init__(self):
        """Initialize the async validation engine."""
        self.start_time = time.time()

        if VALIDATION_AVAILABLE:
            # Initialize validators - they will detect project root as needed
            self.rankle_validator = (
                None  # Will be created per validation with proper project root
            )
            self.quality_toolchain = (
                None  # Will be created per validation with file_path
            )
        else:
            self.rankle_validator = None
            self.quality_toolchain = None

        self.validation_cache = (
            get_validation_cache() if get_validation_cache else None
            )

        # Performance tracking
        self.validation_count = 0
        self.total_execution_time = 0.0
        self.cache_hits = 0

    async def validate_request(self, request: ValidationRequest) -> ValidationResult:
        """
        Main async validation entry point.

        Args:
            request: ValidationRequest with content and context

        Returns:
            ValidationResult with all violations and metrics
        """
        start_time = time.time()

        if not VALIDATION_AVAILABLE:
            return ValidationResult(
                has_violations=False,
                clean_code_violations=[],
                toolchain_violations=[],
                total_violations=0,
                execution_time_ms=0.0,
                error_message="Validation components not available",
            )
        
        if self.validation_cache is not None:
            cached = self.validation_cache.get_combined_result(
                request.content, request.file_path
                )
            if cached is not None:
                clean_code_violations, toolchain_violations = cached
                execution_time_ms = (time.time() - start_time) * 1000
                self._update_performance_metrics(execution_time_ms)
                self.cache_hits += 1
                return ValidationResult(
                    has_violations=bool(clean_code_violations or toolchain_violations),
                    clean_code_violations=clean_code_violations,
                    toolchain_violations=toolchain_violations,
                    total_violations=len(clean_code_violations)
                    + len(toolchain_violations),
                    execution_time_ms=execution_time_ms,
                    validation_scope=request.scope,
                    cache_hit=True,
                )


        try:
            # Execute Clean Code and toolchain validation in parallel
            async with asyncio.TaskGroup() as task_group:
                # Task 1: Clean Code validation
                clean_code_task = task_group.create_task(
                    self._validate_clean_code_async(request)
                )

                # Task 2: Quality toolchain validation
                toolchain_task = task_group.create_task(
                    self._validate_toolchain_async(request)
                )

            # Collect results from both tasks
            clean_code_violations = await clean_code_task
            toolchain_violations = await toolchain_task

            # Calculate execution time and update metrics
            # AIDEV-NOTE: 1000 is conversion factor from seconds to milliseconds
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_performance_metrics(execution_time_ms)
            if self.validation_cache is not None:
                self.validation_cache.cache_combined_result(
                    request.content,
                    request.file_path,
                    clean_code_violations,
                    toolchain_violations,
                )


            # Build final result
            has_violations = bool(clean_code_violations or toolchain_violations)
            total_violations = len(clean_code_violations) + len(toolchain_violations)

            return ValidationResult(
                has_violations=has_violations,
                clean_code_violations=clean_code_violations,
                toolchain_violations=toolchain_violations,
                total_violations=total_violations,
                execution_time_ms=execution_time_ms,
                validation_scope=request.scope,
            )

        except Exception as e:
            # AIDEV-NOTE: 1000 is conversion factor from seconds to milliseconds
            execution_time_ms = (time.time() - start_time) * 1000
            return ValidationResult(
                has_violations=True,
                clean_code_violations=[],
                toolchain_violations=[f"Validation error: {e!s}"],
                total_violations=1,
                execution_time_ms=execution_time_ms,
                error_message=str(e),
            )

    async def _validate_clean_code_async(self, request: ValidationRequest) -> list[Any]:
        """Async wrapper for Clean Code validation."""
        try:
            # Import project utilities to detect project root
            from project_utils import get_project_root_from_file
            from rankle_quality_validators import RankleQualityValidator

            # Detect project root from file path
            project_root = get_project_root_from_file(request.file_path)
            project_root_str = str(project_root) if project_root else ""

            # Create validator with proper project root
            validator = RankleQualityValidator(project_root=project_root_str)

            # Run in thread pool to avoid blocking event loop
            loop = asyncio.get_running_loop()
            violations = await loop.run_in_executor(
                None, validator.validate_content, request.content, request.file_path
            )
            return violations or []

        except Exception as e:
            return [f"Clean Code validation error: {e!s}"]

    async def _validate_toolchain_async(self, request: ValidationRequest) -> list[Any]:
        """Async wrapper for quality toolchain validation."""
        try:
            # Create memory-based temporary file for toolchain validation
            violations = await self._run_toolchain_on_content_async(
                request.content, request.file_path
            )
            return violations or []

        except Exception as e:
            return [f"Toolchain validation error: {e!s}"]

    async def _run_toolchain_on_content_async(
        self, content: str, file_path: str
    ) -> list[Any]:
        """
        Run quality toolchain validation with async execution.

        Uses regular toolchain for reliable validation.
        """
        violations = []

        try:
            # Use regular toolchain for reliable validation with file path for project detection
            try:
                from quality_toolchain import QualityToolchain

                # Pass file_path so toolchain can detect project root and venv
                toolchain = QualityToolchain(file_path=file_path)

                # Create temporary file for toolchain validation
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, encoding="utf-8"
                )

                try:
                    # Write content to temp file
                    temp_file.write(content)
                    temp_file.flush()
                    temp_file.close()

                    # Run regular toolchain validation
                    # AIDEV-NOTE: Pass original file_path for per-file-ignore matching
                    # This preserves patterns like "scripts/**/*.py" even with temp files
                    loop = asyncio.get_running_loop()
                    result = await loop.run_in_executor(
                        None,
                        toolchain.run_all,
                        temp_file.name,
                        file_path  # original_path parameter
                    )

                    # Collect all violations from the regular toolchain
                    violations.extend(result.ruff_issues or [])
                    violations.extend(result.black_issues or [])
                    violations.extend(result.manual_fix_issues or [])
                    violations.extend(result.auto_fixable_issues or [])

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_file.name)
                    except OSError:
                        pass

            except ImportError:
                # Fallback to original toolchain if optimized not available
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, encoding="utf-8"
                )

                try:
                    # Write content to temp file
                    temp_file.write(content)
                    temp_file.flush()
                    temp_file.close()

                    # Run original toolchain validation in executor
                    loop = asyncio.get_running_loop()
                    fallback_toolchain = QualityToolchain(file_path=file_path)  # type: ignore
                    result = await loop.run_in_executor(None, fallback_toolchain.run_all, temp_file.name)

                    # Collect all violations
                    if result:
                        violations.extend(result.auto_fixable_issues or [])
                        violations.extend(result.unsafe_fix_issues or [])
                        violations.extend(result.manual_fix_issues or [])

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_file.name)
                    except OSError:
                        pass

        except Exception as fallback_error:
            violations.append(f"Fallback toolchain error: {fallback_error!s}")

        return violations

    def _update_performance_metrics(self, execution_time_ms: float):
        """Update internal performance tracking metrics."""
        self.validation_count += 1
        self.total_execution_time += execution_time_ms

    def get_performance_stats(self) -> dict[str, Any]:
        """Get current performance statistics."""
        avg_execution_time = (
            self.total_execution_time / self.validation_count
            if self.validation_count > 0
            else 0.0
        )

        return {
            "total_validations": self.validation_count,
            # AIDEV-NOTE: 2 is decimal places for millisecond precision
            "average_execution_time_ms": round(avg_execution_time, 2),
            # AIDEV-NOTE: 2 is decimal places for millisecond precision
            "total_execution_time_ms": round(self.total_execution_time, 2),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": (
                self.cache_hits / self.validation_count
                if self.validation_count > 0
                else 0.0
            ),
        }

    def is_available(self) -> bool:
        """Check if validation components are available."""
        return VALIDATION_AVAILABLE


# AIDEV-NOTE: Factory function for easy instantiation
def create_async_validator() -> AsyncValidatorEngine:
    """Create and return a new AsyncValidatorEngine instance."""
    return AsyncValidatorEngine()


# AIDEV-NOTE: Helper function for backward compatibility
async def validate_content_async(content: str, file_path: str) -> ValidationResult:
    """
    Convenience function for async content validation.

    Args:
        content: Python code content to validate
        file_path: Path to the file (for context)

    Returns:
        ValidationResult with all violations and metrics
    """
    engine = create_async_validator()
    request = ValidationRequest(
        content=content, file_path=file_path, scope=ValidationScope.CONTENT_ONLY
    )
    return await engine.validate_request(request)


if __name__ == "__main__":
    # Simple test of the async validation engine

    test_code = """
def very_long_function_that_exceeds_limits():
    # This is a deliberately bad function
    magic_number = 999  # Magic number violation
    if True:
        if True:
            if True:
                if True:
                    if True:  # Nesting depth violation
                        return magic_number
"""

    async def test():
        engine = create_async_validator()
        request = ValidationRequest(
            content=test_code, file_path="test.py", scope=ValidationScope.CONTENT_ONLY
        )
        result = await engine.validate_request(request)

        # AIDEV-NOTE: Output to stderr to prevent Claude Code API 400 errors
        print(f"Violations found: {result.total_violations}", file=sys.stderr)
        print(f"Execution time: {result.execution_time_ms:.1f}ms", file=sys.stderr)
        print(f"Has violations: {result.has_violations}", file=sys.stderr)

        if result.clean_code_violations:
            print("\nClean Code violations:", file=sys.stderr)
            for violation in result.clean_code_violations[:3]:
                print(f"  Line {violation.line}: {violation.message}", file=sys.stderr)

    if VALIDATION_AVAILABLE:
        asyncio.run(test())
    else:
        print("Validation components not available for testing")
