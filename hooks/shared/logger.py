"""
Simple logger for SuperClaude-Lite hooks.

Provides structured logging of hook events for later analysis.
Focuses on capturing hook lifecycle, decisions, and errors in a
structured format without any analysis or complex features.
"""

import glob
import json
from json_utils import safe_json_dumps # type: ignore
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Import configuration loader
try:
    from yaml_loader import UnifiedConfigLoader
except ImportError:
    # Fallback if .yaml_loader is not available
    UnifiedConfigLoader = None


class HookLogger:
    """Simple logger for SuperClaude-Lite hooks."""

    def __init__(self, log_dir: str = None, retention_days: int = None):
        """
        Initialize the logger.

        Args:
            log_dir: Directory to store log files. Defaults to cache/logs/
            retention_days: Number of days to keep log files. Defaults to 30.
        """
        # Load configuration
        self.config = self._load_config()

        # Check if logging is enabled
        if not self.config.get("logging", {}).get("enabled", True):
            self.enabled = False
            return

        self.enabled = True

        # Set up log directory
        if log_dir is None:
            # Get SuperClaude-Lite root directory (2 levels up from shared/)
            root_dir = Path(__file__).parent.parent.parent
            log_dir_config = (
                self.config.get("logging", {})
                .get("file_settings", {})
                .get("log_directory", "cache/logs")
            )
            log_dir = root_dir / log_dir_config

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Log retention settings
        if retention_days is None:
            retention_days = (
                self.config.get("logging", {})
                .get("file_settings", {})
                .get("retention_days", 30)
            )
        self.retention_days = retention_days

        # Session ID for correlating events - shared across all hooks in the same Claude Code session
        self.session_id = self._get_or_create_session_id()

        # Set up Python logger
        self._setup_logger()

        # Clean up old logs on initialization
        self._cleanup_old_logs()

    def _load_config(self) -> dict[str, Any]:
        """Load logging configuration from YAML file."""
        if UnifiedConfigLoader is None:
            # Return default configuration if loader not available
            return {
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "file_settings": {
                        "log_directory": "cache/logs",
                        "retention_days": 30,
                    },
                }
            }

        try:
            # Get project root
            root_dir = Path(__file__).parent.parent.parent
            loader = UnifiedConfigLoader(root_dir)

            # Load logging configuration
            config = loader.load_yaml("logging")
            return config or {}
        except Exception:
            # Return default configuration on error
            return {
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "file_settings": {
                        "log_directory": "cache/logs",
                        "retention_days": 30,
                    },
                }
            }

    def _get_or_create_session_id(self) -> str:
        """
        Get or create a shared session ID for correlation across all hooks.

        Checks in order:
        1. Environment variable CLAUDE_SESSION_ID
        2. Session file in cache directory
        3. Generate new UUID and save to session file

        Returns:
            8-character session ID string
        """
        # Check environment variable first
        env_session_id = os.environ.get("CLAUDE_SESSION_ID")
        if env_session_id:
            return env_session_id[:8]  # Truncate to 8 characters for consistency

        # Check for session file in cache directory
        cache_dir = self.log_dir.parent  # logs are in cache/logs, so parent is cache/
        session_file = cache_dir / "session_id"

        try:
            if session_file.exists():
                session_id = session_file.read_text(encoding="utf-8").strip()
                # Validate it's a reasonable session ID (8 chars, alphanumeric)
                if len(session_id) == 8 and session_id.replace("-", "").isalnum():
                    return session_id
        except OSError:
            # If we can't read the file, generate a new one
            pass

        # Generate new session ID and save it
        new_session_id = str(uuid.uuid4())[:8]
        try:
            # Ensure cache directory exists
            cache_dir.mkdir(parents=True, exist_ok=True)
            session_file.write_text(new_session_id, encoding="utf-8")
        except OSError:
            # If we can't write the file, just return the ID
            # The session won't be shared, but at least this instance will work
            pass

        return new_session_id

    def _setup_logger(self):
        """Set up the Python logger with JSON formatting."""
        self.logger = logging.getLogger("superclaude_lite_hooks")

        # Set log level from configuration
        log_level_str = self.config.get("logging", {}).get("level", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        self.logger.setLevel(log_level)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create daily log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"superclaude-lite-{today}.log"

        # File handler
        handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        handler.setLevel(logging.INFO)

        # Simple formatter - just output the message (which is already JSON)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def _create_event(
        self, event_type: str, hook_name: str, data: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Create a structured event."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session": self.session_id,
            "hook": hook_name,
            "event": event_type,
        }

        if data:
            event["data"] = data

        return event

    def _should_log_event(self, hook_name: str, event_type: str) -> bool:
        """Check if this event should be logged based on configuration."""
        if not self.enabled:
            return False

        # Check hook-specific configuration
        hook_config = self.config.get("hook_configuration", {}).get(hook_name, {})
        if not hook_config.get("enabled", True):
            return False

        # Check event type configuration
        hook_logging = self.config.get("logging", {}).get("hook_logging", {})
        event_mapping = {
            "start": "log_lifecycle",
            "end": "log_lifecycle",
            "decision": "log_decisions",
            "error": "log_errors",
        }

        config_key = event_mapping.get(event_type, "log_lifecycle")
        return hook_logging.get(config_key, True)

    def log_hook_start(self, hook_name: str, context: dict[str, Any] | None = None):
        """Log the start of a hook execution."""
        if not self._should_log_event(hook_name, "start"):
            return

        event = self._create_event("start", hook_name, context)
        self.logger.info(safe_json_dumps(event))

    def log_hook_end(
        self,
        hook_name: str,
        duration_ms: int,
        success: bool,
        result: dict[str, Any] | None = None,
    ):
        """Log the end of a hook execution."""
        if not self._should_log_event(hook_name, "end"):
            return

        data = {"duration_ms": duration_ms, "success": success}
        if result:
            data["result"] = result

        event = self._create_event("end", hook_name, data)
        self.logger.info(safe_json_dumps(event))

    def log_decision(
        self, hook_name: str, decision_type: str, choice: str, reason: str
    ):
        """Log a decision made by a hook."""
        if not self._should_log_event(hook_name, "decision"):
            return

        data = {"type": decision_type, "choice": choice, "reason": reason}
        event = self._create_event("decision", hook_name, data)
        self.logger.info(safe_json_dumps(event))

    def log_error(
        self, hook_name: str, error: str, context: dict[str, Any] | None = None
    ):
        """Log an error that occurred in a hook."""
        if not self._should_log_event(hook_name, "error"):
            return

        data = {"error": error}
        if context:
            data["context"] = context

        event = self._create_event("error", hook_name, data)
        self.logger.info(safe_json_dumps(event))

    def _cleanup_old_logs(self):
        """Remove log files older than retention_days."""
        if self.retention_days <= 0:
            return

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        # Find all log files
        log_pattern = self.log_dir / "superclaude-lite-*.log"
        for log_file in glob.glob(str(log_pattern)):
            try:
                # Extract date from filename
                filename = os.path.basename(log_file)
                date_str = filename.replace("superclaude-lite-", "").replace(".log", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                # Remove if older than cutoff
                if file_date < cutoff_date:
                    os.remove(log_file)

            except (ValueError, OSError):
                # Skip files that don't match expected format or can't be removed
                continue


# Global logger instance
_logger = None


def get_logger() -> HookLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = HookLogger()
    return _logger


# Convenience functions for easy hook integration
def log_hook_start(hook_name: str, context: dict[str, Any] | None = None):
    """Log the start of a hook execution."""
    get_logger().log_hook_start(hook_name, context)


def log_hook_end(
    hook_name: str,
    duration_ms: int,
    success: bool,
    result: dict[str, Any] | None = None,
):
    """Log the end of a hook execution."""
    get_logger().log_hook_end(hook_name, duration_ms, success, result)


def log_decision(hook_name: str, decision_type: str, choice: str, reason: str):
    """Log a decision made by a hook."""
    get_logger().log_decision(hook_name, decision_type, choice, reason)


def log_error(hook_name: str, error: str, context: dict[str, Any] | None = None):
    """Log an error that occurred in a hook."""
    get_logger().log_error(hook_name, error, context)
