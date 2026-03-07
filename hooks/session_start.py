#!/usr/bin/env python3
"""
SuperClaude-Lite Session Start Hook

Implements SESSION_LIFECYCLE.md + FLAGS.md logic for intelligent session bootstrap.
Performance target: <50ms execution time.

This hook runs at the start of every Claude Code session and provides:
- Smart project context loading with framework exclusion
- Automatic mode detection and activation
- MCP server intelligence routing
- User preference adaptation
- Performance-optimized initialization
"""

import json
import sys
import time
from pathlib import Path

# Add shared directory to Python path for imports
HOOK_DIR = Path(__file__).parent
SHARED_DIR = HOOK_DIR / "shared"
sys.path.insert(0, str(SHARED_DIR))

# Import shared utilities
from json_utils import safe_json_dump, safe_json_dumps
from logger import log_decision, log_error, log_hook_end, log_hook_start
from yaml_loader import config_loader
from hook_response import SessionStartResponse


class SessionStartHook:
    """
    Session start hook implementing SuperClaude intelligence.

    Responsibilities:
    - Initialize session with project context
    - Apply user preferences and learned adaptations
    - Activate appropriate modes and MCP servers
    - Set up compression and performance optimization
    - Track session metrics and performance
    """

    def __init__(self):
        start_time = time.time()

        # Initialize only essential components immediately
        # AIDEV-NOTE: Speculative modules removed (pattern_detector, mcp_intelligence, compression, learning)

        # Use installation directory for cache
        import os

        cache_dir = Path(os.path.expanduser("~/.claude/cache"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_dir = cache_dir

        # Load hook-specific configuration from SuperClaude config
        self.hook_config = config_loader.get_hook_config("session_start")

        # Load session configuration (from YAML if exists, otherwise use hook config)
        try:
            self.session_config = config_loader.load_config("session")
        except FileNotFoundError:
            # Fall back to hook configuration if YAML file not found
            self.session_config = self.hook_config.get("configuration", {})

        # Performance tracking using configuration
        self.initialization_time = (time.time() - start_time) * 1000
        self.performance_target_ms = config_loader.get_hook_config(
            "session_start", "performance_target_ms", 50
        )

    def _normalize_operation_type(self, operation_type):
        """Normalize operation type to string value for JSON serialization."""
        # AIDEV-NOTE: Simplified without OperationType enum (framework_logic removed)
        if hasattr(operation_type, "value"):
            return operation_type.value
        if isinstance(operation_type, str):
            return operation_type
        return "read"  # Default fallback


    def initialize_session(self, session_context: dict) -> dict:
        """
        Initialize session with SuperClaude intelligence.

        Args:
            session_context: Session initialization context from Claude Code

        Returns:
            Enhanced session configuration
        """
        start_time = time.time()

        # Log hook start
        log_hook_start(
            "session_start",
            {
                "project_path": session_context.get("project_path", "unknown"),
                "user_id": session_context.get("user_id", "anonymous"),
                "has_previous_session": bool(
                    session_context.get("previous_session_id")
                ),
            },
        )

        try:
            # Extract session context
            context = self._extract_session_context(session_context)

            # Detect patterns and operation intent
            detection_result = self._detect_session_patterns(context)

            # Apply learned adaptations
            enhanced_recommendations = self._apply_learning_adaptations(
                context, detection_result
            )

            # Create MCP activation plan
            mcp_plan = self._create_mcp_activation_plan(
                context, enhanced_recommendations
            )

            # Configure compression strategy
            compression_config = self._configure_compression(context)

            # Generate session configuration
            session_config = self._generate_session_config(
                context, enhanced_recommendations, mcp_plan, compression_config
            )

            # Record learning event
            self._record_session_learning(context, session_config)

            # Detect and activate modes
            activated_modes = self._activate_intelligent_modes(
                context, enhanced_recommendations
            )

            # Log mode activation decisions
            for mode in activated_modes:
                log_decision(
                    "session_start",
                    "mode_activation",
                    mode["name"],
                    f"Activated based on: {mode.get('trigger', 'automatic detection')}",
                )

            # Configure MCP server activation
            mcp_configuration = self._configure_mcp_servers(context, activated_modes)

            # Log MCP server decisions
            if mcp_configuration.get("enabled_servers"):
                log_decision(
                    "session_start",
                    "mcp_server_activation",
                    ",".join(mcp_configuration["enabled_servers"]),
                    f"Project type: {context.get('project_type', 'unknown')}",
                )

            # Performance validation
            execution_time = (time.time() - start_time) * 1000
            session_config["performance_metrics"] = {
                "initialization_time_ms": execution_time,
                "target_met": execution_time < self.performance_target_ms,
                "efficiency_score": self._calculate_initialization_efficiency(
                    execution_time
                ),
            }

            # Persist session context to cache for other hooks
            session_id = context["session_id"]
            session_file_path = self._cache_dir / f"session_{session_id}.json"
            try:
                with open(session_file_path, "w") as f:
                    safe_json_dump(session_config, f, indent=2)
            except Exception as e:
                # Log error but don't fail session initialization
                log_error(
                    "session_start",
                    f"Failed to persist session context: {e!s}",
                    {"session_id": session_id},
                )

            # Log successful completion
            log_hook_end(
                "session_start",
                int(execution_time),
                True,
                {
                    "project_type": context.get("project_type", "unknown"),
                    "modes_activated": [m["name"] for m in activated_modes],
                    "mcp_servers": mcp_configuration.get("enabled_servers", []),
                },
            )

            return session_config

        except Exception as e:
            # Log error
            execution_time = (time.time() - start_time) * 1000
            log_error(
                "session_start",
                str(e),
                {"project_path": session_context.get("project_path", "unknown")},
            )
            log_hook_end("session_start", int(execution_time), False)

            # Graceful fallback on error
            return self._create_fallback_session_config(session_context, str(e))

    def _extract_session_context(self, session_data: dict) -> dict:
        """Extract and enrich session context."""
        context = {
            "session_id": session_data.get("session_id", "unknown"),
            "project_path": session_data.get("project_path", ""),
            "user_input": session_data.get("user_input", ""),
            "conversation_length": session_data.get("conversation_length", 0),
            "resource_usage_percent": session_data.get("resource_usage_percent", 0),
            "is_continuation": session_data.get("is_continuation", False),
            "previous_session_id": session_data.get("previous_session_id"),
            "timestamp": time.time(),
        }

        # Detect project characteristics
        if context["project_path"]:
            project_path = Path(context["project_path"])
            context.update(self._analyze_project_structure(project_path))

        # Analyze user input for intent
        if context["user_input"]:
            context.update(self._analyze_user_intent(context["user_input"]))

        return context

    def _analyze_project_structure(self, project_path: Path) -> dict:
        """Analyze project structure for intelligent configuration."""
        analysis = {
            "project_type": "unknown",
            "has_tests": False,
            "has_frontend": False,
            "has_backend": False,
            "framework_detected": None,
            "file_count_estimate": 0,
            "directory_count_estimate": 0,
            "is_production": False,
        }

        try:
            if not project_path.exists():
                return analysis

            # Quick file/directory count (limited for performance)
            files = list(project_path.rglob("*"))[:100]  # Limit for performance
            analysis["file_count_estimate"] = len([f for f in files if f.is_file()])
            analysis["directory_count_estimate"] = len([f for f in files if f.is_dir()])

            # Detect project type
            if (project_path / "package.json").exists():
                analysis["project_type"] = "nodejs"
                analysis["has_frontend"] = True
            elif (project_path / "pyproject.toml").exists() or (
                project_path / "setup.py"
            ).exists():
                analysis["project_type"] = "python"
            elif (project_path / "Cargo.toml").exists():
                analysis["project_type"] = "rust"
            elif (project_path / "go.mod").exists():
                analysis["project_type"] = "go"

            # Check for tests
            test_patterns = ["test", "tests", "__tests__", "spec"]
            analysis["has_tests"] = any(
                (project_path / pattern).exists()
                or any(pattern in str(f) for f in files[:20])
                for pattern in test_patterns
            )

            # Check for production indicators
            prod_indicators = [
                ".env.production",
                "docker-compose.yml",
                "Dockerfile",
                ".github",
            ]
            analysis["is_production"] = any(
                (project_path / indicator).exists() for indicator in prod_indicators
            )

            # Framework detection (quick check)
            if analysis["project_type"] == "nodejs":
                package_json = project_path / "package.json"
                if package_json.exists():
                    try:
                        with open(package_json) as f:
                            pkg_data = json.load(f)
                            deps = {
                                **pkg_data.get("dependencies", {}),
                                **pkg_data.get("devDependencies", {}),
                            }

                            if "react" in deps:
                                analysis["framework_detected"] = "react"
                            elif "vue" in deps:
                                analysis["framework_detected"] = "vue"
                            elif "angular" in deps:
                                analysis["framework_detected"] = "angular"
                            elif "express" in deps:
                                analysis["has_backend"] = True
                    except:
                        pass

        except Exception:
            # Return partial analysis on error
            pass

        return analysis

    def _analyze_user_intent(self, user_input: str) -> dict:
        """Analyze user input for session intent and complexity."""
        # AIDEV-NOTE: Simplified intent analysis without OperationType enum (framework_logic removed)
        intent_analysis = {
            "operation_type": "read",
            "complexity_score": 0.0,
            "brainstorming_likely": False,
            "user_expertise": "intermediate",
            "urgency": "normal",
        }

        user_lower = user_input.lower()

        # Detect operation type
        if any(
            word in user_lower for word in ["build", "create", "implement", "develop"]
        ):
            intent_analysis["operation_type"] = "build"
            intent_analysis["complexity_score"] += 0.3
        elif any(
            word in user_lower for word in ["fix", "debug", "troubleshoot", "solve"]
        ):
            intent_analysis["operation_type"] = "analyze"
            intent_analysis["complexity_score"] += 0.2
        elif any(
            word in user_lower for word in ["refactor", "restructure", "reorganize"]
        ):
            intent_analysis["operation_type"] = "refactor"
            intent_analysis["complexity_score"] += 0.4
        elif any(word in user_lower for word in ["test", "validate", "check"]):
            intent_analysis["operation_type"] = "test"
            intent_analysis["complexity_score"] += 0.1

        # Detect brainstorming needs
        brainstorm_indicators = [
            "not sure",
            "thinking about",
            "maybe",
            "possibly",
            "could we",
            "brainstorm",
            "explore",
            "figure out",
            "new project",
            "startup idea",
        ]
        intent_analysis["brainstorming_likely"] = any(
            indicator in user_lower for indicator in brainstorm_indicators
        )

        # Complexity indicators
        complexity_indicators = [
            "complex",
            "complicated",
            "comprehensive",
            "entire",
            "whole",
            "system-wide",
            "architecture",
            "multiple",
            "many",
            "several",
        ]
        for indicator in complexity_indicators:
            if indicator in user_lower:
                intent_analysis["complexity_score"] += 0.2

        intent_analysis["complexity_score"] = min(
            intent_analysis["complexity_score"], 1.0
        )

        # Detect urgency
        if any(word in user_lower for word in ["urgent", "asap", "quickly", "fast"]):
            intent_analysis["urgency"] = "high"
        elif any(
            word in user_lower for word in ["when you can", "no rush", "eventually"]
        ):
            intent_analysis["urgency"] = "low"

        return intent_analysis

    def _detect_session_patterns(self, context: dict) -> dict:
        """Detect patterns for intelligent session configuration."""
        # AIDEV-NOTE: Pattern detection removed (was speculative) - return minimal defaults
        return {
            "pattern_matches": [],
            "recommended_modes": [],
            "recommended_mcp_servers": [],
            "suggested_flags": [],
            "confidence_score": 0.0,
        }

    def _apply_learning_adaptations(
        self, context: dict, detection_result: dict
    ) -> dict:
        """Apply learned adaptations to enhance recommendations."""
        # AIDEV-NOTE: Learning engine removed (was speculative) - return detection results as-is
        return {
            "recommended_modes": detection_result["recommended_modes"],
            "recommended_mcp_servers": detection_result["recommended_mcp_servers"],
            "suggested_flags": detection_result["suggested_flags"],
            "applied_adaptations": [],
        }

    def _apply_user_preferences(self, recommendations: dict, context: dict):
        """Apply stored user preferences to recommendations."""
        # AIDEV-NOTE: Learning engine removed (was speculative) - no preference storage
        pass

    def _create_mcp_activation_plan(self, context: dict, recommendations: dict) -> dict:
        """Create MCP server activation plan."""
        # AIDEV-NOTE: MCP intelligence removed (was speculative) - return minimal defaults
        return {
            "servers_to_activate": [],
            "activation_order": [],
            "estimated_cost_ms": 0,
            "coordination_strategy": "none",
            "fallback_strategy": "none",
        }

    def _configure_compression(self, context: dict) -> dict:
        """Configure compression strategy for the session."""
        # AIDEV-NOTE: Compression engine removed (was speculative) - return minimal defaults
        return {
            "compression_level": "minimal",
            "estimated_savings": 0,
            "quality_impact": 0.0,
            "selective_compression_enabled": False,
        }

    def _generate_session_config(
        self,
        context: dict,
        recommendations: dict,
        mcp_plan: dict,
        compression_config: dict,
    ) -> dict:
        """Generate comprehensive session configuration."""
        config = {
            "session_id": context["session_id"],
            "superclaude_enabled": True,
            "initialization_timestamp": context["timestamp"],
            # Mode configuration
            "active_modes": recommendations.get("recommended_modes", []),
            "mode_configurations": self._get_mode_configurations(recommendations),
            # MCP server configuration
            "mcp_servers": {
                "enabled_servers": mcp_plan["servers_to_activate"],
                "activation_order": mcp_plan["activation_order"],
                "coordination_strategy": mcp_plan["coordination_strategy"],
            },
            # Compression configuration
            "compression": compression_config,
            # Performance configuration
            "performance": {
                "resource_monitoring_enabled": True,
                "optimization_targets": {},  # framework_logic removed
                "delegation_threshold": (
                    0.4 if context.get("complexity_score", 0) > 0.4 else 0.6
                ),
            },
            # Learning configuration
            "learning": {
                "adaptation_enabled": True,
                "effectiveness_tracking": True,
                "applied_adaptations": recommendations.get("applied_adaptations", []),
            },
            # Context preservation
            "context": {
                "project_type": context.get("project_type", "unknown"),
                "complexity_score": context.get("complexity_score", 0.0),
                "brainstorming_mode": context.get("brainstorming_likely", False),
                "user_expertise": context.get("user_expertise", "intermediate"),
            },
            # Quality gates
            "quality_gates": self._configure_quality_gates(context),
            # Session metadata
            "metadata": {
                "framework_version": "1.0.0",
                "hook_version": "session_start_1.0",
                "configuration_source": "superclaude_intelligence",
            },
        }

        return config

    def _get_mode_configurations(self, recommendations: dict) -> dict:
        """Get specific configuration for activated modes."""
        mode_configs = {}

        for mode in recommendations.get("recommended_modes", []):
            if mode == "brainstorming":
                mode_configs[mode] = {
                    "max_rounds": 15,
                    "convergence_threshold": 0.85,
                    "auto_handoff_enabled": True,
                }
            elif mode == "task_management":
                mode_configs[mode] = {
                    "delegation_enabled": True,
                    "wave_orchestration": True,
                    "auto_checkpoints": True,
                }
            elif mode == "token_efficiency":
                mode_configs[mode] = {
                    "compression_level": "adaptive",
                    "symbol_systems_enabled": True,
                    "selective_preservation": True,
                }

        return mode_configs

    def _configure_quality_gates(self, context: dict) -> list:
        """Configure quality gates based on context."""
        # AIDEV-NOTE: framework_logic removed - quality gates handled by Rankle validator
        return []

    def _record_session_learning(self, context: dict, session_config: dict):
        """Record session initialization for learning."""
        # AIDEV-NOTE: Learning engine removed (was speculative) - no event recording
        pass

    def _create_fallback_session_config(
        self, session_context: dict, error: str
    ) -> dict:
        """Create fallback configuration on error."""
        return {
            "session_id": session_context.get("session_id", "unknown"),
            "superclaude_enabled": False,
            "fallback_mode": True,
            "error": error,
            "basic_config": {
                "compression_level": "minimal",
                "mcp_servers_enabled": False,
                "learning_disabled": True,
            },
            "performance_metrics": {
                "execution_time_ms": 0,
                "target_met": False,
                "error_occurred": True,
            },
        }

    def _activate_intelligent_modes(self, context: dict, recommendations: dict) -> list:
        """Activate intelligent modes based on context and recommendations."""
        activated_modes = []

        # Add brainstorming mode if likely
        if context.get("brainstorming_likely", False):
            activated_modes.append({"name": "brainstorming", "trigger": "user input"})

        # Add task management mode if recommended
        if "task_management" in recommendations.get("recommended_modes", []):
            activated_modes.append(
                {"name": "task_management", "trigger": "pattern detection"}
            )

        # Add token efficiency mode if recommended
        if "token_efficiency" in recommendations.get("recommended_modes", []):
            activated_modes.append(
                {"name": "token_efficiency", "trigger": "pattern detection"}
            )

        return activated_modes

    def _configure_mcp_servers(self, context: dict, activated_modes: list) -> dict:
        """Configure MCP servers based on context and activated modes."""
        # AIDEV-NOTE: MCP intelligence removed (was speculative) - return minimal defaults
        return {
            "enabled_servers": [],
            "activation_order": [],
            "coordination_strategy": "none",
        }

    def _calculate_initialization_efficiency(self, execution_time: float) -> float:
        """Calculate initialization efficiency score."""
        return (
            1.0 - (execution_time / self.performance_target_ms)
            if execution_time < self.performance_target_ms
            else 0.0
        )


def main():
    """Main hook execution function."""
    try:
        # Read session data from stdin
        session_data = json.loads(sys.stdin.read())

        # Initialize and run hook
        hook = SessionStartHook()
        result = hook.initialize_session(session_data)

        # Use spec-compliant response
        response = SessionStartResponse(
            initialization_data=result,
            system_message="SessionStart hook completed"
        )
        response.output_and_exit(exit_code=0)

    except Exception as e:
        # Return error response (fail-safe mode)
        response = SessionStartResponse(
            initialization_data={"superclaude_enabled": False, "fallback_mode": True},
            system_message=f"⚠️ Hook error: {str(e)}"
        )
        response.output_and_exit(exit_code=0)


if __name__ == "__main__":
    main()
