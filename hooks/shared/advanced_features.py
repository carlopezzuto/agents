"""
Advanced hook features: updatedInput, continue control, and user confirmations.

Implements advanced Claude Code hooks features:
- Path normalization and auto-fixing
- Critical error flow control
- Destructive operation confirmations
- Parameter validation and modification
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class PathNormalizer:
    """Normalizes and fixes file paths for tools."""

    def __init__(self, cwd: str):
        """Initialize with current working directory."""
        self.cwd = Path(cwd)

    def normalize_path(self, path: str) -> Tuple[str, bool]:
        """Normalize a file path to absolute form.

        Args:
            path: Input file path (relative or absolute)

        Returns:
            Tuple of (normalized_path, was_modified)
        """
        path_obj = Path(path)

        # Already absolute and normalized
        if path_obj.is_absolute():
            return str(path_obj), False

        # Convert relative to absolute
        absolute_path = (self.cwd / path_obj).resolve()
        return str(absolute_path), True

    def fix_tool_input_paths(self, tool_name: str, tool_input: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """Fix file paths in tool input.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tuple of (modified_input, was_modified)
        """
        modified = False
        updated_input = tool_input.copy()

        # Tools with file_path parameter
        if tool_name in ["Read", "Write", "Edit"] and "file_path" in tool_input:
            normalized, changed = self.normalize_path(tool_input["file_path"])
            if changed:
                updated_input["file_path"] = normalized
                modified = True

        # Bash tool with paths in command
        elif tool_name == "Bash" and "command" in tool_input:
            # Could parse command for file paths, but risky to modify
            # Skip for now to avoid breaking commands
            pass

        # Glob tool with path parameter
        elif tool_name == "Glob" and "path" in tool_input:
            normalized, changed = self.normalize_path(tool_input["path"])
            if changed:
                updated_input["path"] = normalized
                modified = True

        return updated_input, modified


class DestructiveOperationDetector:
    """Detects potentially destructive operations that need confirmation."""

    DESTRUCTIVE_TOOLS = {
        "Write": "Creates or overwrites files",
        "Edit": "Modifies existing files",
        "Bash": "Executes shell commands",
    }

    DESTRUCTIVE_BASH_PATTERNS = [
        "rm ", "rmdir", "delete", "DROP TABLE", "DROP DATABASE",
        "truncate", ">/dev/null", ">null", "format ", "mkfs",
        "dd if=", "shred", "wipe"
    ]

    def __init__(self, ask_for_confirmation: bool = False):
        """Initialize detector.

        Args:
            ask_for_confirmation: Whether to request user confirmation for destructive ops
        """
        self.ask_for_confirmation = ask_for_confirmation

    def is_destructive(self, tool_name: str, tool_input: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if operation is destructive.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tuple of (is_destructive, reason)
        """
        if tool_name not in self.DESTRUCTIVE_TOOLS:
            return False, ""

        # Write tool is always destructive (overwrites files)
        if tool_name == "Write":
            file_path = tool_input.get("file_path", "unknown")
            return True, f"Will create/overwrite file: {file_path}"

        # Edit tool modifies existing files
        if tool_name == "Edit":
            file_path = tool_input.get("file_path", "unknown")
            return True, f"Will modify file: {file_path}"

        # Bash with destructive commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            for pattern in self.DESTRUCTIVE_BASH_PATTERNS:
                if pattern in command:
                    return True, f"Destructive bash command detected: {pattern.strip()}"

        return False, ""

    def should_ask_confirmation(self, tool_name: str, tool_input: Dict[str, Any]) -> Tuple[bool, str]:
        """Determine if user confirmation is needed.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tuple of (should_ask, reason)
        """
        if not self.ask_for_confirmation:
            return False, ""

        is_destructive, reason = self.is_destructive(tool_name, tool_input)
        if is_destructive:
            return True, f"⚠️ Destructive operation detected: {reason}\n\nProceed?"

        return False, ""


class CriticalErrorDetector:
    """Detects critical errors that should stop hook processing."""

    def __init__(self):
        """Initialize detector."""
        pass

    def is_critical_error(self, error: Exception) -> Tuple[bool, str]:
        """Check if error is critical enough to stop processing.

        Args:
            error: The exception that occurred

        Returns:
            Tuple of (is_critical, reason)
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # JSON parsing errors are critical
        if "JSON" in error_type:
            return True, f"Critical JSON parsing error: {error_msg}"

        # File system errors in validation
        if "FileNotFoundError" in error_type and "validation" in error_msg.lower():
            return True, f"Critical validation file missing: {error_msg}"

        # Out of memory errors
        if "MemoryError" in error_type:
            return True, "Critical memory error - system resources exhausted"

        # Permission errors for required files
        if "PermissionError" in error_type:
            return True, f"Critical permission error: {error_msg}"

        # Most errors are non-critical (fail-safe)
        return False, f"Non-critical error: {error_msg}"


class ContextInjector:
    """Injects context into user prompts."""

    def __init__(self, cwd: str):
        """Initialize with current working directory."""
        self.cwd = Path(cwd)

    def get_project_context(self) -> Optional[str]:
        """Get project context from README, CLAUDE.md, etc.

        Returns:
            Project context string or None
        """
        context_files = ["CLAUDE.md", "README.md", ".clauderc"]

        for filename in context_files:
            context_file = self.cwd / filename
            if context_file.exists():
                try:
                    content = context_file.read_text(encoding="utf-8")
                    # Return first 1000 chars to avoid overwhelming prompt
                    return f"\n---\n📁 Project Context from {filename}:\n{content[:1000]}\n---\n"
                except Exception:
                    continue

        return None

    def inject_context(self, user_prompt: str) -> Tuple[str, bool]:
        """Inject context into user prompt if beneficial.

        Args:
            user_prompt: Original user prompt

        Returns:
            Tuple of (modified_prompt, was_modified)
        """
        # Only inject if prompt seems to need context
        needs_context = any(
            keyword in user_prompt.lower()
            for keyword in ["help", "how", "what is", "explain", "show", "architecture"]
        )

        if not needs_context:
            return user_prompt, False

        context = self.get_project_context()
        if context:
            modified = f"{context}\n{user_prompt}"
            return modified, True

        return user_prompt, False


class SessionReporter:
    """Generates session summary reports."""

    def __init__(self):
        """Initialize reporter."""
        pass

    def generate_session_summary(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive session summary.

        Args:
            session_data: Session data from Stop/SessionEnd hooks

        Returns:
            Summary dictionary with metrics
        """
        summary = {
            "session_id": session_data.get("session_id", "unknown"),
            "timestamp": session_data.get("timestamp"),
            "metrics": {
                "tools_used": 0,
                "files_modified": 0,
                "validations_performed": 0,
                "violations_found": 0,
                "learning_updates": 0,
            },
            "recommendations": [],
        }

        # Add recommendations based on session
        if summary["metrics"]["violations_found"] > 0:
            summary["recommendations"].append(
                "Review quality violations to maintain code standards"
            )

        if summary["metrics"]["tools_used"] > 50:
            summary["recommendations"].append(
                "Consider breaking down complex tasks into smaller sessions"
            )

        return summary
