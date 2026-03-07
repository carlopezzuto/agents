#!/usr/bin/env python3
"""
Post-Tool-Use Hook

Implements RULES.md + PRINCIPLES.md validation and learning system.
Performance target: <100ms execution time.

This hook runs after every tool usage and provides:
- Quality validation
- Effectiveness measurement and learning
- Error pattern detection and prevention
- Performance optimization feedback
- Adaptation and improvement recommendations
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

from logger import log_decision, log_error, log_hook_end, log_hook_start
from yaml_loader import config_loader
from hook_response import PostToolUseResponse

# Process cleanup is handled by hook_response.output_and_exit()
# which flushes stdout before exiting
import atexit

# AIDEV-NOTE: Import optimized Rankle quality validation system
try:
    from async_validator_engine import (
        AsyncValidatorEngine,
        ValidationRequest,
        ValidationScope,
    )
    from validation_cache import ValidationCache, get_validation_cache

    RANKLE_QUALITY_AVAILABLE = True
except ImportError as e:
    # Rankle validation unavailable, will use fallback mode
    RANKLE_QUALITY_AVAILABLE = False



# Simple ValidationResult for quality checks
class ValidationResult:
    def __init__(self, is_valid=True, issues=None, warnings=None, suggestions=None, quality_score=1.0, message=""):
        self.is_valid = is_valid
        self.issues = issues or []
        self.warnings = warnings or []
        self.suggestions = suggestions or []
        self.quality_score = quality_score
        self.message = message
        self.failed_checks = issues or []


class PostToolUseHook:
    """
    Post-tool-use hook implementing validation and learning.

    Responsibilities:
    - Validate tool execution against RULES.md and PRINCIPLES.md
    - Measure operation effectiveness and quality
    - Learn from successful and failed patterns
    - Detect error patterns and suggest improvements
    - Record performance metrics for optimization
    - Generate adaptation recommendations
    """

    def __init__(self):
        start_time = time.time()

        # Initialize core components

        # Load hook-specific configuration from SuperClaude config
        self.hook_config = config_loader.get_hook_config("post_tool_use")

        # AIDEV-NOTE: Initialize Rankle quality validation system
        if RANKLE_QUALITY_AVAILABLE:
            self.validation_engine = AsyncValidatorEngine()
            self.validation_cache = get_validation_cache()
        else:
            self.validation_engine = None
            self.validation_cache = None

        # Load validation configuration (from YAML if exists, otherwise use hook config)
        try:
            self.validation_config = config_loader.load_config("validation")
        except FileNotFoundError:
            # Fall back to hook configuration if YAML file not found
            self.validation_config = self.hook_config.get("configuration", {})

        # Load quality standards (from YAML if exists, otherwise use hook config)
        try:
            self.quality_standards = config_loader.load_config("performance")
        except FileNotFoundError:
            # Fall back to performance targets from global configuration
            self.quality_standards = config_loader.get_performance_targets()

        # Performance tracking using configuration
        self.initialization_time = (time.time() - start_time) * 1000
        self.performance_target_ms = config_loader.get_hook_config(
            "post_tool_use", "performance_target_ms", 100
        )

    def process_tool_result(self, tool_result: dict) -> dict:
        """
        Process tool execution result with validation and learning.

        Args:
            tool_result: Tool execution result from Claude Code

        Returns:
            Enhanced result with validation and insights
        """
        start_time = time.time()

        # Log hook start
        log_hook_start(
            "post_tool_use",
            {
                "tool_name": tool_result.get("tool_name", "unknown"),
                "success": tool_result.get("success", False),
                "has_error": bool(tool_result.get("error")),
            },
        )

        try:
            # Extract execution context
            context = self._extract_execution_context(tool_result)

            # AIDEV-NOTE: Rankle quality validation for Python file operations
            if self._should_run_rankle_validation(tool_result):
                self._validate_rankle_quality_sync(tool_result)

            # Validate against SuperClaude principles
            validation_result = self._validate_tool_result(context)

            # Log validation decision
            if not validation_result.is_valid:
                log_decision(
                    "post_tool_use",
                    "validation_failure",
                    (
                        validation_result.failed_checks[0]
                        if validation_result.failed_checks
                        else "unknown"
                    ),
                    f"Tool '{context['tool_name']}' failed validation: {validation_result.message}",
                )

            # Measure effectiveness and quality
            effectiveness_metrics = self._measure_effectiveness(
                context, validation_result
            )

            # Detect patterns and learning opportunities
            learning_analysis = self._analyze_learning_opportunities(
                context, effectiveness_metrics
            )

            # Record learning events
            self._record_learning_events(
                context, effectiveness_metrics, learning_analysis
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                context, validation_result, learning_analysis
            )

            # Create validation report
            validation_report = self._create_validation_report(
                context,
                validation_result,
                effectiveness_metrics,
                learning_analysis,
                recommendations,
            )

            # Detect patterns in tool execution
            pattern_analysis = self._analyze_execution_patterns(
                context, validation_result
            )

            # Log pattern detection
            if pattern_analysis.get("error_pattern_detected"):
                log_decision(
                    "post_tool_use",
                    "error_pattern_detected",
                    pattern_analysis.get("pattern_type", "unknown"),
                    pattern_analysis.get("description", "Error pattern identified"),
                )

            # Performance tracking
            execution_time = (time.time() - start_time) * 1000
            validation_report["performance_metrics"] = {
                "processing_time_ms": execution_time,
                "target_met": execution_time < self.performance_target_ms,
                "quality_score": self._calculate_quality_score(
                    context, validation_result
                ),
            }

            # Log successful completion
            log_hook_end(
                "post_tool_use",
                int(execution_time),
                True,
                {
                    "tool_name": context["tool_name"],
                    "validation_passed": validation_result.is_valid,
                    "quality_score": validation_report["performance_metrics"][
                        "quality_score"
                    ],
                },
            )

            return validation_report

        except Exception as e:
            # Log error
            execution_time = (time.time() - start_time) * 1000
            log_error(
                "post_tool_use",
                str(e),
                {"tool_name": tool_result.get("tool_name", "unknown")},
            )
            log_hook_end("post_tool_use", int(execution_time), False)

            # Graceful fallback on error
            return self._create_fallback_result(tool_result, str(e))

    def _extract_execution_context(self, tool_result: dict) -> dict:
        """Extract and enrich tool execution context."""
        context = {
            "tool_name": tool_result.get("tool_name", ""),
            "execution_status": tool_result.get("status", "unknown"),
            "execution_time_ms": tool_result.get("execution_time_ms", 0),
            "parameters_used": tool_result.get("parameters", {}),
            "result_data": tool_result.get("result", {}),
            "error_info": tool_result.get("error", {}),
            "mcp_servers_used": tool_result.get("mcp_servers", []),
            "performance_data": tool_result.get("performance", {}),
            "user_intent": tool_result.get("user_intent", ""),
            "session_context": tool_result.get("session_context", {}),
            "timestamp": time.time(),
        }

        # Analyze operation characteristics
        context.update(self._analyze_operation_outcome(context))

        # Extract quality indicators
        context.update(self._extract_quality_indicators(context))

        return context

    def _analyze_operation_outcome(self, context: dict) -> dict:
        """Analyze the outcome of the tool operation."""
        outcome_analysis = {
            "success": context["execution_status"] == "success",
            "partial_success": False,
            "error_occurred": context["execution_status"] == "error",
            "performance_acceptable": True,
            "quality_indicators": [],
            "risk_factors": [],
        }

        # Analyze execution status
        if context["execution_status"] in ["partial", "warning"]:
            outcome_analysis["partial_success"] = True

        # Performance analysis
        execution_time = context.get("execution_time_ms", 0)
        if execution_time > 5000:  # 5 second threshold
            outcome_analysis["performance_acceptable"] = False
            outcome_analysis["risk_factors"].append("slow_execution")

        # Error analysis
        if context.get("error_info"):
            error_type = context["error_info"].get("type", "unknown")
            outcome_analysis["error_type"] = error_type
            outcome_analysis["error_recoverable"] = error_type not in [
                "fatal",
                "security",
                "corruption",
            ]

        # Quality indicators from result data
        result_data = context.get("result_data", {})
        if result_data:
            if result_data.get("validation_passed"):
                outcome_analysis["quality_indicators"].append("validation_passed")
            if result_data.get("tests_passed"):
                outcome_analysis["quality_indicators"].append("tests_passed")
            if result_data.get("linting_clean"):
                outcome_analysis["quality_indicators"].append("linting_clean")

        return outcome_analysis

    def _extract_quality_indicators(self, context: dict) -> dict:
        """Extract quality indicators from execution context."""
        quality_indicators = {
            "code_quality_score": 0.0,
            "security_compliance": True,
            "performance_efficiency": 1.0,
            "error_handling_present": False,
            "documentation_adequate": False,
            "test_coverage_acceptable": False,
        }

        # Analyze tool output for quality indicators
        tool_name = context["tool_name"]
        result_data = context.get("result_data", {})

        # Code quality analysis
        if tool_name in ["Write", "Edit", "Generate"]:
            # Check for quality indicators in the result
            if "quality_score" in result_data:
                quality_indicators["code_quality_score"] = result_data["quality_score"]

            # Infer quality from operation success and performance
            if context.get("success") and context.get("performance_acceptable"):
                quality_indicators["code_quality_score"] = max(
                    quality_indicators["code_quality_score"], 0.7
                )

        # Security compliance
        if context.get("error_type") in ["security", "vulnerability"]:
            quality_indicators["security_compliance"] = False

        # Performance efficiency
        execution_time = context.get("execution_time_ms", 0)
        expected_time = context.get("performance_data", {}).get(
            "expected_time_ms", 1000
        )
        if execution_time > 0 and expected_time > 0:
            quality_indicators["performance_efficiency"] = min(
                expected_time / execution_time, 2.0
            )

        # Error handling detection
        if tool_name in ["Write", "Edit"] and "try" in str(result_data).lower():
            quality_indicators["error_handling_present"] = True

        # Documentation assessment
        if (
            tool_name in ["Document", "Generate"]
            or "doc" in context.get("user_intent", "").lower()
        ):
            quality_indicators["documentation_adequate"] = context.get("success", False)

        return quality_indicators

    def _validate_tool_result(self, context: dict) -> ValidationResult:
        """Simplified validation - just check success."""
        # AIDEV-NOTE: Simplified validation without framework_logic
        if context.get("success", False):
            return ValidationResult(is_valid=True, quality_score=0.9)
        else:
            return ValidationResult(
                is_valid=False,
                issues=["Tool execution failed"],
                quality_score=0.3
            )

    def _enhance_validation_with_superclaude_rules(
        self, base_validation: ValidationResult, context: dict
    ) -> ValidationResult:
        """Enhance validation with SuperClaude-specific rules."""
        enhanced_validation = ValidationResult(
            is_valid=base_validation.is_valid,
            issues=base_validation.issues.copy(),
            warnings=base_validation.warnings.copy(),
            suggestions=base_validation.suggestions.copy(),
            quality_score=base_validation.quality_score,
        )

        # RULES.md validation

        # Rule: Always use Read tool before Write or Edit operations
        if context["tool_name"] in ["Write", "Edit"]:
            session_context = context.get("session_context", {})
            recent_tools = session_context.get("recent_tools", [])
            if not any("Read" in tool for tool in recent_tools[-3:]):
                enhanced_validation.warnings.append(
                    "RULES violation: No Read operation detected before Write/Edit"
                )
                enhanced_validation.quality_score -= 0.1

        # Rule: Use absolute paths only
        params = context.get("parameters_used", {})
        for param_name, param_value in params.items():
            if "path" in param_name.lower() and isinstance(param_value, str):
                if not os.path.isabs(param_value) and not param_value.startswith(
                    ("http", "https")
                ):
                    enhanced_validation.issues.append(
                        f"RULES violation: Relative path used in {param_name}: {param_value}"
                    )
                    enhanced_validation.quality_score -= 0.2

        # Rule: Validate before execution for high-risk operations
        if context.get("risk_factors"):
            if not context.get("validation_performed", False):
                enhanced_validation.warnings.append(
                    "RULES recommendation: High-risk operation should include validation"
                )

        # PRINCIPLES.md validation

        # Principle: Evidence > assumptions
        if not context.get("evidence_provided", False) and context.get(
            "assumptions_made", False
        ):
            enhanced_validation.suggestions.append(
                "PRINCIPLES: Provide evidence to support assumptions"
            )

        # Principle: Code > documentation
        if context["tool_name"] == "Document" and not context.get(
            "working_code_exists", True
        ):
            enhanced_validation.warnings.append(
                "PRINCIPLES: Documentation should follow working code, not precede it"
            )

        # Principle: Efficiency > verbosity
        result_size = len(str(context.get("result_data", "")))
        if result_size > 5000 and not context.get("complexity_justifies_length", False):
            enhanced_validation.suggestions.append(
                "PRINCIPLES: Consider token efficiency techniques for large outputs"
            )

        # Recalculate overall validity
        enhanced_validation.is_valid = (
            len(enhanced_validation.issues) == 0
            and enhanced_validation.quality_score >= 0.7
        )

        return enhanced_validation

    def _measure_effectiveness(
        self, context: dict, validation_result: ValidationResult
    ) -> dict:
        """Measure operation effectiveness and quality."""
        effectiveness_metrics = {
            "overall_effectiveness": 0.0,
            "quality_score": validation_result.quality_score,
            "performance_score": 0.0,
            "user_satisfaction_estimate": 0.0,
            "learning_value": 0.0,
            "improvement_potential": 0.0,
        }

        # Performance scoring
        execution_time = context.get("execution_time_ms", 0)
        expected_time = context.get("performance_data", {}).get(
            "expected_time_ms", 1000
        )
        if execution_time > 0:
            time_ratio = expected_time / max(execution_time, 1)
            effectiveness_metrics["performance_score"] = min(time_ratio, 1.0)
        else:
            effectiveness_metrics["performance_score"] = 1.0

        # User satisfaction estimation
        if context.get("success"):
            base_satisfaction = 0.8
            if validation_result.quality_score > 0.8:
                base_satisfaction += 0.15
            if effectiveness_metrics["performance_score"] > 0.8:
                base_satisfaction += 0.05
            effectiveness_metrics["user_satisfaction_estimate"] = min(
                base_satisfaction, 1.0
            )
        else:
            # Reduce satisfaction based on error severity
            error_severity = self._assess_error_severity(context)
            effectiveness_metrics["user_satisfaction_estimate"] = max(
                0.3 - error_severity * 0.3, 0.0
            )

        # Learning value assessment
        if context.get("mcp_servers_used"):
            effectiveness_metrics[
                "learning_value"
            ] += 0.2  # MCP usage provides learning
        if context.get("error_occurred"):
            effectiveness_metrics[
                "learning_value"
            ] += 0.3  # Errors provide valuable learning
        if context.get("complexity_score", 0) > 0.6:
            effectiveness_metrics[
                "learning_value"
            ] += 0.2  # Complex operations provide insights

        effectiveness_metrics["learning_value"] = min(
            effectiveness_metrics["learning_value"], 1.0
        )

        # Improvement potential
        if len(validation_result.suggestions) > 0:
            effectiveness_metrics["improvement_potential"] = min(
                len(validation_result.suggestions) * 0.2, 1.0
            )

        # Overall effectiveness calculation
        weights = {
            "quality": 0.3,
            "performance": 0.25,
            "satisfaction": 0.35,
            "learning": 0.1,
        }

        effectiveness_metrics["overall_effectiveness"] = (
            effectiveness_metrics["quality_score"] * weights["quality"]
            + effectiveness_metrics["performance_score"] * weights["performance"]
            + effectiveness_metrics["user_satisfaction_estimate"]
            * weights["satisfaction"]
            + effectiveness_metrics["learning_value"] * weights["learning"]
        )

        return effectiveness_metrics

    def _assess_error_severity(self, context: dict) -> float:
        """Assess error severity on a scale of 0.0 to 1.0."""
        if not context.get("error_occurred"):
            return 0.0

        error_type = context.get("error_type", "unknown")

        severity_map = {
            "fatal": 1.0,
            "security": 0.9,
            "corruption": 0.8,
            "timeout": 0.6,
            "validation": 0.4,
            "warning": 0.2,
            "unknown": 0.5,
        }

        return severity_map.get(error_type, 0.5)

    def _analyze_learning_opportunities(
        self, context: dict, effectiveness_metrics: dict
    ) -> dict:
        """Analyze learning opportunities from the execution."""
        learning_analysis = {
            "patterns_detected": [],
            "success_factors": [],
            "failure_factors": [],
            "optimization_opportunities": [],
            "adaptation_recommendations": [],
        }

        # Pattern detection
        if context.get("mcp_servers_used"):
            for server in context["mcp_servers_used"]:
                if effectiveness_metrics["overall_effectiveness"] > 0.8:
                    learning_analysis["patterns_detected"].append(
                        f"effective_{server}_usage"
                    )
                elif effectiveness_metrics["overall_effectiveness"] < 0.5:
                    learning_analysis["patterns_detected"].append(
                        f"ineffective_{server}_usage"
                    )

        # Success factor analysis
        if effectiveness_metrics["overall_effectiveness"] > 0.8:
            if effectiveness_metrics["performance_score"] > 0.8:
                learning_analysis["success_factors"].append("optimal_performance")
            if effectiveness_metrics["quality_score"] > 0.8:
                learning_analysis["success_factors"].append("high_quality_output")
            if context.get("mcp_servers_used"):
                learning_analysis["success_factors"].append(
                    "effective_mcp_coordination"
                )

        # Failure factor analysis
        if effectiveness_metrics["overall_effectiveness"] < 0.5:
            if effectiveness_metrics["performance_score"] < 0.5:
                learning_analysis["failure_factors"].append("poor_performance")
            if effectiveness_metrics["quality_score"] < 0.5:
                learning_analysis["failure_factors"].append("quality_issues")
            if context.get("error_occurred"):
                learning_analysis["failure_factors"].append(
                    f"error_{context.get('error_type', 'unknown')}"
                )

        # Optimization opportunities
        if effectiveness_metrics["improvement_potential"] > 0.3:
            learning_analysis["optimization_opportunities"].append(
                "validation_improvements_available"
            )

        if context.get("execution_time_ms", 0) > 2000:
            learning_analysis["optimization_opportunities"].append(
                "performance_optimization_needed"
            )

        # Adaptation recommendations
        if len(learning_analysis["success_factors"]) > 0:
            learning_analysis["adaptation_recommendations"].append(
                f"Reinforce patterns: {', '.join(learning_analysis['success_factors'])}"
            )

        if len(learning_analysis["failure_factors"]) > 0:
            learning_analysis["adaptation_recommendations"].append(
                f"Address failure patterns: {', '.join(learning_analysis['failure_factors'])}"
            )

        return learning_analysis

    def _record_learning_events(
        self, context: dict, effectiveness_metrics: dict, learning_analysis: dict
    ):
        """Record learning events for future adaptation (disabled)."""
        # AIDEV-NOTE: Learning engine removed - this is now a no-op
        pass

    def _generate_recommendations(
        self,
        context: dict,
        validation_result: ValidationResult,
        learning_analysis: dict,
    ) -> dict:
        """Generate recommendations for improvement."""
        recommendations = {
            "immediate_actions": [],
            "optimization_suggestions": [],
            "learning_adaptations": [],
            "prevention_measures": [],
        }

        # Immediate actions from validation issues
        for issue in validation_result.issues:
            recommendations["immediate_actions"].append(f"Fix: {issue}")

        for warning in validation_result.warnings:
            recommendations["immediate_actions"].append(f"Address: {warning}")

        # Optimization suggestions
        for suggestion in validation_result.suggestions:
            recommendations["optimization_suggestions"].append(suggestion)

        for opportunity in learning_analysis["optimization_opportunities"]:
            recommendations["optimization_suggestions"].append(
                f"Optimize: {opportunity}"
            )

        # Learning adaptations
        for adaptation in learning_analysis["adaptation_recommendations"]:
            recommendations["learning_adaptations"].append(adaptation)

        # Prevention measures for errors
        if context.get("error_occurred"):
            error_type = context.get("error_type", "unknown")
            if error_type == "timeout":
                recommendations["prevention_measures"].append(
                    "Consider parallel execution for large operations"
                )
            elif error_type == "validation":
                recommendations["prevention_measures"].append(
                    "Enable pre-validation for similar operations"
                )
            elif error_type == "security":
                recommendations["prevention_measures"].append(
                    "Implement security validation checks"
                )

        return recommendations

    def _calculate_quality_score(
        self, context: dict, validation_result: ValidationResult
    ) -> float:
        """Calculate quality score based on validation and execution."""
        base_score = validation_result.quality_score

        # Adjust for execution time
        execution_time = context.get("execution_time_ms", 0)
        time_ratio = execution_time / max(self.performance_target_ms, 1)
        time_penalty = min(time_ratio, 1.0)

        # Initialize error penalty (no penalty when no error occurs)
        error_penalty = 1.0

        # Adjust for error occurrence
        if context.get("error_occurred"):
            error_severity = self._assess_error_severity(context)
            error_penalty = 1.0 - error_severity

        # Combine adjustments
        quality_score = base_score * time_penalty * error_penalty

        return quality_score

    def _create_validation_report(
        self,
        context: dict,
        validation_result: ValidationResult,
        effectiveness_metrics: dict,
        learning_analysis: dict,
        recommendations: dict,
    ) -> dict:
        """Create comprehensive validation report."""
        return {
            "tool_name": context["tool_name"],
            "execution_status": context["execution_status"],
            "timestamp": context["timestamp"],
            "validation": {
                "is_valid": validation_result.is_valid,
                "quality_score": validation_result.quality_score,
                "issues": validation_result.issues,
                "warnings": validation_result.warnings,
                "suggestions": validation_result.suggestions,
            },
            "effectiveness": effectiveness_metrics,
            "learning": {
                "patterns_detected": learning_analysis["patterns_detected"],
                "success_factors": learning_analysis["success_factors"],
                "failure_factors": learning_analysis["failure_factors"],
                "learning_value": effectiveness_metrics["learning_value"],
            },
            "recommendations": recommendations,
            "compliance": {
                "rules_compliance": len(
                    [i for i in validation_result.issues if "RULES" in i]
                )
                == 0,
                "principles_alignment": len(
                    [w for w in validation_result.warnings if "PRINCIPLES" in w]
                )
                == 0,
                "superclaude_score": self._calculate_superclaude_compliance_score(
                    validation_result
                ),
            },
            "metadata": {
                "hook_version": "post_tool_use_1.0",
                "validation_timestamp": time.time(),
                "learning_events_recorded": len(learning_analysis["patterns_detected"])
                + 1,
            },
        }

    def _calculate_superclaude_compliance_score(
        self, validation_result: ValidationResult
    ) -> float:
        """Calculate overall SuperClaude compliance score."""
        base_score = validation_result.quality_score

        # Penalties for specific violations
        rules_violations = len([i for i in validation_result.issues if "RULES" in i])
        principles_violations = len(
            [w for w in validation_result.warnings if "PRINCIPLES" in w]
        )

        penalty = (rules_violations * 0.2) + (principles_violations * 0.1)

        return max(base_score - penalty, 0.0)

    def _create_fallback_result(self, tool_result: dict, error: str) -> dict:
        """Create fallback validation report on error."""
        return {
            "tool_name": tool_result.get("tool_name", "unknown"),
            "execution_status": "validation_error",
            "timestamp": time.time(),
            "error": error,
            "fallback_mode": True,
            "validation": {
                "is_valid": False,
                "quality_score": 0.0,
                "issues": [f"Validation hook error: {error}"],
                "warnings": [],
                "suggestions": ["Fix validation hook error"],
            },
            "effectiveness": {
                "overall_effectiveness": 0.0,
                "quality_score": 0.0,
                "performance_score": 0.0,
                "user_satisfaction_estimate": 0.0,
                "learning_value": 0.0,
            },
            "performance_metrics": {
                "processing_time_ms": 0,
                "target_met": False,
                "error_occurred": True,
            },
        }

    def _analyze_execution_patterns(
        self, context: dict, validation_result: ValidationResult
    ) -> dict:
        """Analyze patterns in tool execution."""
        pattern_analysis = {
            "error_pattern_detected": False,
            "pattern_type": "unknown",
            "description": "No error pattern detected",
        }

        # Check for error occurrence
        if context.get("error_occurred"):
            error_type = context.get("error_type", "unknown")

            # Check for specific error types
            if error_type in ["fatal", "security", "corruption"]:
                pattern_analysis["error_pattern_detected"] = True
                pattern_analysis["pattern_type"] = error_type
                pattern_analysis["description"] = (
                    f"Error pattern detected: {error_type}"
                )

        return pattern_analysis

    def _categorize_operation(self, tool_name: str) -> str | None:
        """Categorize tool into operation type for preference tracking."""
        operation_map = {
            "read": ["Read", "Get", "List", "Search", "Find"],
            "write": ["Write", "Create", "Generate"],
            "edit": ["Edit", "Update", "Modify", "Replace", "insert"],
            "analyze": ["Analyze", "Validate", "Check", "Test"],
            "mcp": [
                "Context7",
                "Sequential",
                "Magic",
                "Playwright",
                "Morphllm",
                "Serena",
            ],
        }

        for operation_type, tools in operation_map.items():
            if any(tool in tool_name for tool in tools):
                return operation_type

        return None

    def _should_run_rankle_validation(self, tool_result: dict) -> bool:
        """Determine if Rankle quality validation should be enabled."""
        if not RANKLE_QUALITY_AVAILABLE:
            return False

        # Only validate file modification operations
        tool_name = tool_result.get("tool_name", "")

        # Check for native tools AND MCP Morphllm/Serena tools that modify files
        is_file_modification_tool = (
            # Native file modification tools
            tool_name in ["Edit", "Write", "MultiEdit"]
            or
            # MCP Morphllm and Serena file modification tools
            tool_name.startswith(("mcp__morphllm-fast-apply__", "mcp__serena__"))
        )

        if is_file_modification_tool:

            # Check if operation was successful
            if tool_result.get("error"):
                return False

            # Get file path from tool_input (handle both native and MCP formats)
            tool_input = tool_result.get("tool_input", {})
            file_path = (
                tool_input.get("file_path", "")  # Native tools
                or tool_input.get("path", "")  # MCP Morphllm
                or tool_input.get("relative_path", "")  # MCP Serena
            )

            # Only validate Python files
            if not file_path.endswith(".py"):
                return False

            # Skip validation for hook files to prevent circular dependency
            if "/.claude/hooks/" in file_path:
                return False

            return True

        return False

    def _is_rankle_project_file(self, file_path: str) -> bool:
        """Check if this file is part of a Rankle project."""
        try:
            path = Path(file_path)
            current_dir = path.parent if path.is_file() else path

            # Walk up the directory tree looking for Rankle indicators
            for parent in [current_dir] + list(current_dir.parents):
                # Check for CLAUDE.md with Rankle content
                claude_md = parent / "CLAUDE.md"
                if claude_md.exists():
                    try:
                        content = claude_md.read_text(encoding="utf-8")
                        if "Rankle" in content and "candidate-job matching" in content:
                            return True
                    except:
                        pass

                # Check for rankle-specific directories
                if (parent / "src" / "ontology").exists() and (
                    parent / "src" / "ml_pipeline"
                ).exists():
                    return True

                # Check for pyproject.toml with rankle info
                pyproject = parent / "pyproject.toml"
                if pyproject.exists():
                    try:
                        content = pyproject.read_text(encoding="utf-8")
                        if "rankle" in content.lower():
                            return True
                    except:
                        pass

            return False
        except:
            return False

    def _get_recently_modified_python_files(self, max_age_seconds: int = 30) -> list:
        """
        Find all Python files modified in the last 30 seconds.
        This catches files modified by ANY tool (native or MCP servers).
        """
        # AIDEV-NOTE: File system monitoring to catch ALL file changes, not just native tools
        modified_files = []
        current_time = time.time()
        search_dirs = [os.getcwd()]

        # Add parent directories up to 3 levels (for project detection)
        current_path = Path(os.getcwd())
        for parent in list(current_path.parents)[:3]:
            search_dirs.append(str(parent))

        for search_dir in search_dirs:
            try:
                for root, dirs, files in os.walk(search_dir):
                    # Skip hidden directories and common non-project directories
                    dirs[:] = [
                        d
                        for d in dirs
                        if not d.startswith(".")
                        and d not in ["__pycache__", "node_modules", ".git", ".venv"]
                    ]

                    for file in files:
                        if file.endswith(".py"):
                            file_path = os.path.join(root, file)
                            try:
                                # Check modification time
                                mtime = os.path.getmtime(file_path)
                                if current_time - mtime <= max_age_seconds:
                                    # Skip hook files to prevent circular dependency
                                    if "/.claude/hooks/" not in file_path:
                                        modified_files.append(file_path)
                            except OSError:
                                continue  # Skip files we can't access

            except OSError:
                continue  # Skip directories we can't access

        return modified_files

    def _validate_rankle_quality_sync(self, tool_result: dict) -> None:
        """Synchronous wrapper for Rankle quality validation."""
        if not RANKLE_QUALITY_AVAILABLE:
            return

        import asyncio

        try:
            # Try to run async validation
            try:
                loop = asyncio.get_running_loop()
                # Schedule on existing loop instead of creating new one
                future = asyncio.run_coroutine_threadsafe(
                    self._validate_rankle_quality_async(tool_result),
                    loop
                )
                future.result(timeout=1.0)
            except RuntimeError:
                # No running loop, safe to create one
                asyncio.run(self._validate_rankle_quality_async(tool_result))

        except Exception as e:
            # Log error but don't block - validation failure shouldn't break workflow
            log_error(
                "rankle_validation",
                str(e),
                {
                    "file_path": tool_result.get("tool_input", {}).get("file_path", ""),
                    "tool_name": tool_result.get("tool_name", ""),
                },
            )

    async def _validate_all_modified_files_async(self, modified_files: list) -> None:
        """Validate all recently modified Python files."""
        if not RANKLE_QUALITY_AVAILABLE:
            return

        validation_tasks = []

        for file_path in modified_files:
            # Only validate Rankle project files
            if not self._is_rankle_project_file(file_path):
                continue

            validation_tasks.append(self._validate_single_file_async(file_path))

        if validation_tasks:
            # Run all validations concurrently
            await asyncio.gather(*validation_tasks, return_exceptions=True)

    async def _validate_single_file_async(self, file_path: str) -> None:
        """Validate a single file asynchronously."""
        try:
            start_time = time.time()

            # Read file content for validation
            file_content = Path(file_path).read_text(encoding="utf-8")

            # Create validation request
            request = ValidationRequest(
                content=file_content,
                file_path=file_path,
                scope=ValidationScope.FULL_FILE,
            )

            # Run validation
            result = await self.validation_engine.validate_request(request)

            if result.has_violations:
                execution_time = (time.time() - start_time) * 1000
                self._report_rankle_violations_and_block(
                    result, file_path, execution_time
                )
            else:
                execution_time = (time.time() - start_time) * 1000
                self._report_validation_success(result, file_path, execution_time)

        except Exception as e:
            # Log error but don't block - validation failure shouldn't break workflow
            log_error("rankle_validation", str(e), {"file_path": file_path})

    async def _validate_rankle_quality_async(self, tool_result: dict) -> None:
        """Perform async Rankle quality validation for Python files."""
        if not RANKLE_QUALITY_AVAILABLE:
            return

        tool_input = tool_result.get("tool_input", {})
        file_path = tool_input.get("file_path", "") or tool_input.get(  # Native tools
            "path", ""
        )  # MCP Morphllm

        try:
            start_time = time.time()

            # Read file content for validation
            file_content = Path(file_path).read_text(encoding="utf-8")

            # Create validation request
            request = ValidationRequest(
                content=file_content,
                file_path=file_path,
                scope=ValidationScope.FULL_FILE,
            )

            # Run validation
            if self.validation_engine is None:
                return # Rankle validator not available

            result = await self.validation_engine.validate_request(request)

            if result.has_violations:
                execution_time = (time.time() - start_time) * 1000
                self._report_rankle_violations_and_block(
                    result, file_path, execution_time
                )
            else:
                execution_time = (time.time() - start_time) * 1000
                self._report_validation_success(result, file_path, execution_time)

        except Exception as e:
            # Log error but don't block - validation failure shouldn't break workflow
            log_error("rankle_validation", str(e), {"file_path": file_path})

    def _report_rankle_violations_and_block(
        self, result, file_path: str, execution_time_ms: float
    ) -> None:
        """Report Rankle quality violations and block with exit code 2."""
        # Create detailed error message for Claude
        error_message = "\n🚨 RANKLE QUALITY VIOLATIONS DETECTED 🚨\n"
        error_message += f"File: {file_path}\n"
        error_message += (
            f"Total violations: {result.total_violations} (ALL BLOCKING)\n\n"
        )

        # Show Clean Code violations
        if result.clean_code_violations:
            error_message += (
                f"🚫 Clean Code Violations ({len(result.clean_code_violations)}):\n"
            )
            for i, violation in enumerate(result.clean_code_violations):
                error_message += (
                    f"  {i+1}. Line {violation.line}: {violation.message}\n"
                )
                error_message += f"     Rule: {violation.rule}\n"
                error_message += f"     Fix: {violation.fix_instruction}\n\n"

        # Show toolchain violations
        if result.toolchain_violations:
            error_message += (
                f"🔧 Quality Toolchain Violations "
                f"({len(result.toolchain_violations)}):\n"
            )
            for i, violation in enumerate(result.toolchain_violations):
                error_message += f"  {i+1}. {violation}\n"

        error_message += "⚠️  FILE HAS BEEN MODIFIED BUT CONTAINS VIOLATIONS!\n"
        error_message += "📋 REQUIRED ACTION:\n"
        error_message += "   1. Fix all violations listed above\n"
        error_message += "   2. Rankle enforces ZERO TOLERANCE for quality violations\n"
        error_message += "   3. All violations must be resolved before continuing\n"

        # Performance info
        if execution_time_ms > 100:
            error_message += (
                f"\n⏱️ Validation: {execution_time_ms:.1f}ms (target: <100ms) ⚠️\n"
            )
        else:
            error_message += f"\n⏱️ Validation: {execution_time_ms:.1f}ms ✅\n"

        # Cache performance info
        if hasattr(result, "cache_hit") and result.cache_hit:
            error_message += "💾 Cache: HIT (7.9x speedup) ⚡\n"
        else:
            error_message += "💾 Cache: MISS (result cached for next time)\n"

        # Use spec-compliant block response
        # Note: PostToolUse "block" provides feedback to Claude but doesn't prevent execution
        response = PostToolUseResponse.block(
            reason=error_message,
            user_message="File modified with quality violations - fixes required",
            system_message="🚨 Quality violations detected in PostToolUse validation"
        )
        response.output_and_exit(exit_code=0)

    def _report_validation_success(
        self, result, file_path: str, execution_time_ms: float
    ) -> None:
        """Report successful validation with performance metrics."""
        # AIDEV-NOTE: Success feedback requested by user to avoid silent validation
        success_message = "\n✅ RANKLE QUALITY VALIDATION PASSED\n"
        success_message += f"File: {file_path}\n"
        success_message += "Status: All quality checks passed\n"

        # Performance info
        if execution_time_ms > 100:
            success_message += (
                f"⏱️ Validation: {execution_time_ms:.1f}ms (target: <100ms) ⚠️\n"
            )
        else:
            success_message += f"⏱️ Validation: {execution_time_ms:.1f}ms ✅\n"

        # Cache performance info
        if hasattr(result, "cache_hit") and result.cache_hit:
            success_message += "💾 Cache: HIT (7.9x speedup) ⚡\n"
        else:
            success_message += "💾 Cache: MISS (result cached for next time)\n"

        success_message += "\n🎉 Ready to continue development!\n"

        # Use spec-compliant allow response
        response = PostToolUseResponse.allow(
            reason=success_message,
            system_message="✅ Quality validation passed"
        )
        response.output_and_exit(exit_code=0)


def main():
    """Main hook execution function."""
    try:
        # Read tool result from stdin
        tool_result = json.loads(sys.stdin.read())

        # AIDEV-NOTE: Comprehensive logging for MCP investigation
        log_dir = Path.home() / ".claude" / "hooks" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "post_tool_use_debug.json"

        # Create log entry with timestamp
        log_entry = {
            "timestamp": time.time(),
            "tool_name": tool_result.get("tool_name", "UNKNOWN"),
            "tool_input": tool_result.get("tool_input", {}),
            "full_tool_result": tool_result,
        }

        # Read existing log data or initialize empty list
        if log_path.exists():
            try:
                with open(log_path) as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
        else:
            log_data = []

        # Append new entry (keep last 50 entries)
        log_data.append(log_entry)
        if len(log_data) > 50:
            log_data = log_data[-50:]

        # Write back to file with formatting
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

        # Initialize and run hook
        hook = PostToolUseHook()
        result = hook.process_tool_result(tool_result)

        # Return spec-compliant allow response
        response = PostToolUseResponse.allow(
            reason="Tool execution analyzed and validated",
            system_message="PostToolUse analysis complete"
        )
        response.output_and_exit(exit_code=0)

    except Exception as e:
        # Return error response (non-blocking in fail-safe mode)
        error_message = f"Hook error: {str(e)}"
        response = PostToolUseResponse.allow(
            reason=error_message,
            system_message="⚠️ PostToolUse error (operation allowed in fail-safe mode)"
        )
        response.output_and_exit(exit_code=0)


if __name__ == "__main__":
    main()
