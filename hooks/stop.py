#!/usr/bin/env python3
"""
SuperClaude-Lite Stop Hook

Implements session analytics + /sc:save logic with performance tracking.
Performance target: <200ms execution time.

This hook runs at session end and provides:
- Comprehensive session analytics and performance metrics
- Learning consolidation and adaptation updates
- Session persistence with intelligent compression
- Performance optimization recommendations
- Quality assessment and improvement suggestions
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add shared directory to Python path for imports
HOOK_DIR = Path(__file__).parent
SHARED_DIR = HOOK_DIR / "shared"
sys.path.insert(0, str(SHARED_DIR))

# Framework imports
from logger import log_decision, log_error, log_hook_end, log_hook_start
from yaml_loader import config_loader
from hook_response import StopResponse

# Process cleanup handled by hook_response
import atexit

async def _check_current_python_files_async() -> tuple[bool, str]:
    """
    Check current Python files for quality violations using direct validation.

    Returns:
        Tuple of (has_violations, message)
    """
    try:
        # AIDEV-NOTE: Import validation components here to avoid import conflicts
        from async_validator_engine import (
            AsyncValidatorEngine,
            ValidationRequest,
            ValidationScope,
        )
        from validation_cache import clear_global_cache

        # AIDEV-NOTE: Clear validation cache to prevent stale violations
        # Stop hook runs at session end, so cache freshness is more important than speed
        clear_global_cache()

        validator = AsyncValidatorEngine()
        if not validator.is_available():
            return False, "Validation not available"

        # Find recently modified Python files (last 10 minutes)
        cwd = os.getcwd()
        recent_files = []
        current_time = time.time()

        # Search current directory and immediate subdirectories
        for root, dirs, files in os.walk(cwd):
            # Limit depth to avoid scanning entire project
            depth = root[len(cwd) :].count(os.sep)
            if depth > 2:
                continue

            # Skip common directories that shouldn't be checked
            dirs[:] = [
                d
                for d in dirs
                if d not in {".git", "__pycache__", ".venv", "venv", "node_modules"}
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        # Check if file was modified in last 10 minutes
                        stat = os.stat(file_path)
                        age_minutes = (current_time - stat.st_mtime) / 60
                        if age_minutes <= 10:
                            recent_files.append(file_path)

        if not recent_files:
            return False, "No recently modified Python files found"

        # Validate each recent file
        violations_found = []
        for file_path in recent_files[:5]:  # Limit to 5 most recent
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                request = ValidationRequest(
                    content=content,
                    file_path=file_path,
                    scope=ValidationScope.FULL_FILE,
                )

                result = await validator.validate_request(request)

                if result.has_violations:
                    violations_found.append(
                        {
                            "file": os.path.relpath(file_path, cwd),
                            "violations": result.total_violations,
                            "clean_code": result.clean_code_violations,
                            "toolchain": result.toolchain_violations,
                        }
                    )

            except Exception:
                # Skip files that can't be validated
                continue

        if violations_found:
            # Format violation message
            total_files = len(violations_found)
            total_violations = sum(v["violations"] for v in violations_found)

            message = f"Cannot exit: {total_violations} quality violations in {total_files} file(s)\n\n"

            for item in violations_found:
                message += f"• {item['file']}: {item['violations']} violation(s)\n"

                # Show examples of violations
                shown = 0
                if item["clean_code"]:
                    for v in item["clean_code"][:2]:
                        if hasattr(v, "line") and hasattr(v, "message"):
                            message += f"  - Line {v.line}: {v.message}\n"
                            shown += 1

                if shown < 2 and item["toolchain"]:
                    for v in item["toolchain"][: 2 - shown]:
                        message += f"  - {v}\n"

            message += "\nFix these violations before exiting."
            return True, message

        return False, "No violations found"

    except Exception as e:
        # On error, allow stop (don't block on validation errors)
        return False, f"Validation error: {e!s}"


# Removed redundant _check_for_quality_violations function
# PostToolUse already validates files after tool execution, so we only need to check its stderr output


async def main_async():
    """Main hook execution function with async quality validation."""
    try:
        # Check for code quality violations first
        has_violations, message = await _check_current_python_files_async()
        if has_violations:
            print(message, file=sys.stderr)
            sys.exit(2)
        sys.exit(0)
    except Exception as e:
        print(f"Valdiation error: {e}", file=sys.stderr)
        sys.exit(1)        

def main():
    """Main hook execution wrapper."""
    # AIDEV-NOTE: Simplified async handling - hooks are standalone scripts, no existing event loop
    # Claude Code hooks run in fresh Python processes, so asyncio.run() is safe
    try:
        asyncio.run(main_async())
    except Exception as e:
        # Log error and exit cleanly (fail-safe mode)
        print(f"Hook execution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
