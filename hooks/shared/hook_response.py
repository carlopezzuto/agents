"""
Spec-compliant hook response builders for Claude Code hooks.

Implements the official Claude Code hooks specification:
https://docs.claude.com/en/docs/claude-code/hooks

All responses follow the standardized JSON structure with:
- hookSpecificOutput: Hook-specific fields (permissionDecision, decision, etc.)
- continue: Flow control (default: true)
- suppressOutput: Output suppression (default: false)
- systemMessage: Optional message to Claude (visible in conversation)
"""

import json
import sys
from typing import Any, Dict, Optional


class HookResponse:
    """Base class for spec-compliant hook responses."""

    def __init__(
        self,
        hook_event_name: str,
        continue_execution: bool = True,
        suppress_output: bool = False,
        system_message: Optional[str] = None,
    ):
        """Initialize base response.

        Args:
            hook_event_name: Name of the hook event (PreToolUse, PostToolUse, etc.)
            continue_execution: Whether to continue processing after this hook
            suppress_output: Whether to suppress hook output from being shown
            system_message: Optional message to show to Claude/user
        """
        self.hook_event_name = hook_event_name
        self.continue_execution = continue_execution
        self.suppress_output = suppress_output
        self.system_message = system_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary.

        Subclasses should override this to add hookSpecificOutput.
        Base implementation provides minimal hookSpecificOutput.
        """
        response = {
            "hookSpecificOutput": {
                "hookEventName": self.hook_event_name
            },
            "continue": self.continue_execution,
            "suppressOutput": self.suppress_output,
        }

        if self.system_message:
            response["systemMessage"] = self.system_message

        return response

    def output_and_exit(self, exit_code: int = 0) -> None:
        """Output response to stdout and exit.

        Args:
            exit_code: Exit code (0 = success, 2 = blocking error)
        """
        response = self.to_dict()
        print(json.dumps(response, indent=2), file=sys.stdout)
        sys.stdout.flush()
        sys.exit(exit_code)


class PreToolUseResponse(HookResponse):
    """Response for PreToolUse hook (spec-compliant)."""

    def __init__(
        self,
        permission_decision: str,  # "allow" | "deny" | "ask"
        permission_decision_reason: str,
        updated_input: Optional[Dict[str, Any]] = None,
        continue_execution: bool = True,
        suppress_output: bool = False,
        system_message: Optional[str] = None,
    ):
        """Initialize PreToolUse response.

        Args:
            permission_decision: "allow", "deny", or "ask"
            permission_decision_reason: Explanation for the decision
            updated_input: Modified tool parameters (optional)
            continue_execution: Whether to continue after this hook
            suppress_output: Whether to suppress output
            system_message: Optional message to Claude/user
        """
        super().__init__(
            hook_event_name="PreToolUse",
            continue_execution=continue_execution,
            suppress_output=suppress_output,
            system_message=system_message,
        )
        self.permission_decision = permission_decision
        self.permission_decision_reason = permission_decision_reason
        self.updated_input = updated_input

    def to_dict(self) -> Dict[str, Any]:
        """Convert to spec-compliant JSON structure."""
        response = super().to_dict()

        hook_specific = {
            "hookEventName": self.hook_event_name,
            "permissionDecision": self.permission_decision,
            "permissionDecisionReason": self.permission_decision_reason,
        }

        if self.updated_input is not None:
            hook_specific["updatedInput"] = self.updated_input

        response["hookSpecificOutput"] = hook_specific
        return response

    @classmethod
    def allow(
        cls,
        reason: str = "Operation allowed",
        updated_input: Optional[Dict[str, Any]] = None,
        system_message: Optional[str] = None,
    ) -> "PreToolUseResponse":
        """Create an 'allow' response."""
        return cls(
            permission_decision="allow",
            permission_decision_reason=reason,
            updated_input=updated_input,
            system_message=system_message,
        )

    @classmethod
    def deny(
        cls,
        reason: str,
        system_message: Optional[str] = None,
    ) -> "PreToolUseResponse":
        """Create a 'deny' response (blocks operation)."""
        return cls(
            permission_decision="deny",
            permission_decision_reason=reason,
            system_message=system_message,
        )

    @classmethod
    def ask(
        cls,
        reason: str,
        system_message: Optional[str] = None,
    ) -> "PreToolUseResponse":
        """Create an 'ask' response (prompts user for confirmation)."""
        return cls(
            permission_decision="ask",
            permission_decision_reason=reason,
            system_message=system_message,
        )


class PostToolUseResponse(HookResponse):
    """Response for PostToolUse hook (spec-compliant)."""

    def __init__(
        self,
        decision: str,  # "allow" | "block"
        decision_reason: str,
        user_message: Optional[str] = None,
        continue_execution: bool = True,
        suppress_output: bool = False,
        system_message: Optional[str] = None,
    ):
        """Initialize PostToolUse response.

        Args:
            decision: "allow" or "block"
            decision_reason: Explanation for the decision
            user_message: Optional message to show to user
            continue_execution: Whether to continue after this hook
            suppress_output: Whether to suppress output
            system_message: Optional message to Claude
        """
        super().__init__(
            hook_event_name="PostToolUse",
            continue_execution=continue_execution,
            suppress_output=suppress_output,
            system_message=system_message,
        )
        self.decision = decision
        self.decision_reason = decision_reason
        self.user_message = user_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to spec-compliant JSON structure."""
        response = super().to_dict()

        hook_specific = {
            "hookEventName": self.hook_event_name,
            "decision": self.decision,
            "decisionReason": self.decision_reason,
        }

        if self.user_message:
            hook_specific["userMessage"] = self.user_message

        response["hookSpecificOutput"] = hook_specific
        return response

    @classmethod
    def allow(
        cls,
        reason: str = "Operation completed successfully",
        user_message: Optional[str] = None,
        system_message: Optional[str] = None,
    ) -> "PostToolUseResponse":
        """Create an 'allow' response."""
        return cls(
            decision="allow",
            decision_reason=reason,
            user_message=user_message,
            system_message=system_message,
        )

    @classmethod
    def block(
        cls,
        reason: str,
        user_message: Optional[str] = None,
        system_message: Optional[str] = None,
    ) -> "PostToolUseResponse":
        """Create a 'block' response (provides feedback to Claude)."""
        return cls(
            decision="block",
            decision_reason=reason,
            user_message=user_message,
            system_message=system_message,
        )


class SessionStartResponse(HookResponse):
    """Response for SessionStart hook (spec-compliant)."""

    def __init__(
        self,
        initialization_data: Optional[Dict[str, Any]] = None,
        continue_execution: bool = True,
        suppress_output: bool = False,
        system_message: Optional[str] = None,
    ):
        """Initialize SessionStart response.

        Args:
            initialization_data: Optional data for session initialization
            continue_execution: Whether to continue after this hook
            suppress_output: Whether to suppress output
            system_message: Optional message to Claude
        """
        super().__init__(
            hook_event_name="SessionStart",
            continue_execution=continue_execution,
            suppress_output=suppress_output,
            system_message=system_message,
        )
        self.initialization_data = initialization_data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to spec-compliant JSON structure."""
        response = super().to_dict()

        response["hookSpecificOutput"] = {
            "hookEventName": self.hook_event_name,
            "initializationData": self.initialization_data,
        }

        return response


class StopResponse(HookResponse):
    """Response for Stop hook (spec-compliant)."""

    def __init__(
        self,
        summary_data: Optional[Dict[str, Any]] = None,
        continue_execution: bool = True,
        suppress_output: bool = False,
        system_message: Optional[str] = None,
    ):
        """Initialize Stop response.

        Args:
            summary_data: Optional data summarizing the session
            continue_execution: Whether to continue after this hook
            suppress_output: Whether to suppress output
            system_message: Optional message to Claude/user
        """
        super().__init__(
            hook_event_name="Stop",
            continue_execution=continue_execution,
            suppress_output=suppress_output,
            system_message=system_message,
        )
        self.summary_data = summary_data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to spec-compliant JSON structure."""
        response = super().to_dict()

        response["hookSpecificOutput"] = {
            "hookEventName": self.hook_event_name,
            "summaryData": self.summary_data,
        }

        return response


def output_error_response(
    hook_event_name: str,
    error_message: str,
    exit_code: int = 1,
) -> None:
    """Output an error response and exit.

    Args:
        hook_event_name: Name of the hook that errored
        error_message: Error message
        exit_code: Exit code (default: 1 for non-blocking error)
    """
    response = {
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "error": error_message,
        },
        "continue": True,
        "suppressOutput": False,
    }

    print(json.dumps(response, indent=2), file=sys.stdout)
    sys.stdout.flush()
    sys.exit(exit_code)
