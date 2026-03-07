#!/usr/bin/env python3
"""
SubagentStop Hook - Simple Task Tool Completion Tracking

Runs when a Claude Code subagent (Task tool) completes.
Logs completion and validates if task was actually finished.

Inspired by real-world examples (100-150 lines, simple logging).
Official spec: https://docs.claude.com/en/docs/claude-code/hooks
"""

import json
import sys
import time
from pathlib import Path

# Add shared directory to Python path
HOOK_DIR = Path(__file__).parent
SHARED_DIR = HOOK_DIR / "shared"
sys.path.insert(0, str(SHARED_DIR))

from hook_response import HookResponse
from logger import log_hook_start, log_hook_end, log_decision


class SubagentStopHook:
    """Simple subagent completion tracking."""

    def __init__(self):
        """Initialize hook."""
        pass

    def process_subagent_stop(self, subagent_data: dict) -> dict:
        """Process subagent completion.

        Args:
            subagent_data: Dict containing:
                - subagent_id: str
                - task_id: str
                - task_description: str
                - output: str
                - success: bool

        Returns:
            Dict with decision to approve or block
        """
        start_time = time.time()

        # Log hook start
        log_hook_start(
            "subagent_stop",
            {
                "subagent_id": subagent_data.get("subagent_id", "unknown"),
                "task_id": subagent_data.get("task_id", "unknown"),
                "success": subagent_data.get("success", False),
            },
        )

        # Extract task info
        task_description = subagent_data.get("task_description", "")
        output = subagent_data.get("output", "")
        success = subagent_data.get("success", False)

        # AIDEV-NOTE: Task validation prevents premature completion (blocks on TODO/FIXME/placeholders)
        incomplete_markers = [
            "TODO",
            "FIXME",
            "not implemented",
            "to be done",
            "placeholder",
            "coming soon",
        ]

        task_incomplete = any(marker.lower() in output.lower() for marker in incomplete_markers)

        # Determine if we should block (ask subagent to continue)
        should_block = False
        reason = "Task completed successfully"

        if not success:
            should_block = True
            reason = "Subagent reported failure"
        elif task_incomplete:
            should_block = True
            reason = "Task appears incomplete (found TODO/placeholder markers)"
        elif len(output.strip()) < 50:
            should_block = True
            reason = "Output too short - task may be incomplete"

        # Log decision
        log_decision(
            "subagent_stop",
            "completion_check",
            "block" if should_block else "approve",
            reason,
        )

        # Create result
        result = {
            "decision": "block" if should_block else "approve",
            "reason": reason,
            "task_id": subagent_data.get("task_id", "unknown"),
            "completion_validated": not should_block,
        }

        # Log completion
        execution_time = (time.time() - start_time) * 1000
        log_hook_end("subagent_stop", int(execution_time), not should_block)

        return result


def main():
    """Main hook execution function."""
    try:
        # Read subagent data from stdin
        subagent_data = json.loads(sys.stdin.read())

        # Initialize and run hook
        hook = SubagentStopHook()
        result = hook.process_subagent_stop(subagent_data)

        # AIDEV-NOTE: continue_execution=False forces subagent to continue working (see hooks spec)
        # Use spec-compliant response
        if result["decision"] == "block":
            response = HookResponse(
                hook_event_name="SubagentStop",
                continue_execution=False,  # Block subagent from stopping
                system_message=f"🚫 Subagent blocked: {result['reason']}"
            )
        else:
            response = HookResponse(
                hook_event_name="SubagentStop",
                system_message=f"✓ Subagent task completed: {result['reason']}"
            )

        response.output_and_exit(exit_code=0)

    except Exception as e:
        # Return error response (fail-safe mode)
        response = HookResponse(
            hook_event_name="SubagentStop",
            system_message=f"⚠️ Hook error: {str(e)}"
        )
        response.output_and_exit(exit_code=0)


if __name__ == "__main__":
    main()
