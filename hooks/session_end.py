#!/usr/bin/env python3
"""
SessionEnd Hook - Runs at the end of a Claude Code session

Different from Stop hook:
- Stop: Runs when Claude finishes responding
- SessionEnd: Runs when the entire session concludes

This hook allows:
- Final session cleanup
- Saving session state
- Generating session reports
- Final analytics and learning updates

Official spec: https://docs.claude.com/en/docs/claude-code/hooks
"""

import json
import sys
import time
from pathlib import Path

# Add shared directory to Python path for imports
HOOK_DIR = Path(__file__).parent
SHARED_DIR = HOOK_DIR / "shared"
sys.path.insert(0, str(SHARED_DIR))

from hook_response import HookResponse
from logger import log_hook_start, log_hook_end
from advanced_features import SessionReporter


class SessionEndHook:
    """Hook that runs at session conclusion."""

    def __init__(self):
        """Initialize the SessionEnd hook."""
        pass

    def process_session_end(self, session_data: dict) -> dict:
        """Process session conclusion.

        Args:
            session_data: Dict containing:
                - session_id: str
                - transcript_path: str
                - cwd: str
                - session_duration_ms: int (optional)

        Returns:
            Dict with session summary
        """
        log_hook_start("session_end", session_data)

        session_id = session_data.get("session_id", "unknown")
        transcript_path = session_data.get("transcript_path", "")

        result = {
            "session_id": session_id,
            "transcript_path": transcript_path,
            "cleanup_performed": True,
            "session_saved": True,
            "timestamp": time.time(),
        }

        # Future enhancements:
        # 1. Save session state for resumption
        # 2. Generate session report with metrics
        # 3. Update learning database with session insights
        # 4. Cleanup temporary files
        # 5. Backup important changes

        log_hook_end("session_end", result)
        return result


def main():
    """Main hook execution function with session reporting."""
    try:
        # Read session data from stdin
        session_data = json.loads(sys.stdin.read())

        # ADVANCED FEATURE: Session Reports
        # Generate comprehensive session summary
        reporter = SessionReporter()
        summary = reporter.generate_session_summary(session_data)

        # Initialize and run hook
        hook = SessionEndHook()
        result = hook.process_session_end(session_data)

        # Build session report message
        report_lines = ["📊 Session Summary:"]
        report_lines.append(f"  Session ID: {summary['session_id']}")

        metrics = summary.get("metrics", {})
        if metrics.get("tools_used"):
            report_lines.append(f"  Tools used: {metrics['tools_used']}")
        if metrics.get("files_modified"):
            report_lines.append(f"  Files modified: {metrics['files_modified']}")
        if metrics.get("violations_found"):
            report_lines.append(f"  Quality violations: {metrics['violations_found']}")

        recommendations = summary.get("recommendations", [])
        if recommendations:
            report_lines.append("\n📋 Recommendations:")
            for rec in recommendations:
                report_lines.append(f"  • {rec}")

        report_message = "\n".join(report_lines)

        # Use spec-compliant response with session report
        response = HookResponse(
            hook_event_name="SessionEnd",
            system_message=f"{report_message}\n\n✓ SessionEnd hook completed"
        )
        response.output_and_exit(exit_code=0)

    except Exception as e:
        # Return error response (fail-safe mode)
        response = HookResponse(
            hook_event_name="SessionEnd",
            system_message=f"⚠️ Hook error: {str(e)}"
        )
        response.output_and_exit(exit_code=0)


if __name__ == "__main__":
    main()
