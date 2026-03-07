#!/usr/bin/env python3
"""
Pre-Tool-Use Hook
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Add shared directory to Python path for imports
HOOK_DIR = Path(__file__).parent
SHARED_DIR = HOOK_DIR / "shared"
sys.path.insert(0, str(SHARED_DIR))

from logger import log_decision, log_error, log_hook_end, log_hook_start
from yaml_loader import config_loader
from hook_response import PreToolUseResponse
from advanced_features import (
    PathNormalizer,
    DestructiveOperationDetector,
    CriticalErrorDetector
)

from typing import Callable, Optional

# Process cleanup is handled by hook_response.output_and_exit()
# which flushes stdout before exiting
import atexit

AsyncValidatorEngine = None
ValidationRequest = None
ValidationScope = None
ValidationCache = None
get_validation_cache: Optional[Callable[[], ValidationCache]] = None

# AIDEV-NOTE: Import optimized Rankle quality validation system
try:
    from async_validator_engine import (
        AsyncValidatorEngine,
        ValidationRequest,
        ValidationScope,
        ValidationResult
    )
    from validation_cache import ValidationCache, get_validation_cache

    RANKLE_QUALITY_AVAILABLE = True
except ImportError:    
    RANKLE_QUALITY_AVAILABLE = False


class PreToolUseHook:
    """
    Pre-tool-use hook.

    Responsibilities:
    - Analyze tool usage context and requirements
    - Implement fallback strategies for server failures
    - Track tool effectiveness and performance metrics
    """

    def __init__(self):
        start_time = time.time()

        # Load hook-specific configuration from SuperClaude config
        self.hook_config = config_loader.get_hook_config("pre_tool_use")

        # Load orchestrator configuration (from YAML if exists, otherwise use hook config)
        try:
            self.orchestrator_config = config_loader.load_config("orchestrator")
        except FileNotFoundError:
            # Fall back to hook configuration if YAML file not found
            self.orchestrator_config = self.hook_config.get("configuration", {})

        # Load performance configuration (from YAML if exists, otherwise use hook config)
        try:
            self.performance_config = config_loader.load_config("performance")
        except FileNotFoundError:
            # Fall back to performance targets from global configuration
            self.performance_config = config_loader.get_performance_targets()

        # Performance tracking using configuration
        self.initialization_time = (time.time() - start_time) * 1000
        self.performance_target_ms = config_loader.get_hook_config(
            "pre_tool_use", "performance_target_ms", 200
        )

    def process_tool_use(self, tool_request: dict) -> dict:
        """
        Process tool use request with intelligent routing.

        Args:
            tool_request: Tool usage request from Claude Code

        Returns:
            Enhanced tool configuration with SuperClaude intelligence
        """
        start_time = time.time()

        # Log hook start
        log_hook_start(
            "pre_tool_use",
            {
                "tool_name": tool_request.get("tool_name", "unknown"),
                "has_parameters": bool(tool_request.get("parameters")),
            },
        )

        try:
            # Extract tool context
            context = self._extract_tool_context(tool_request)

            # Analyze tool requirements and capabilities
            requirements = self._analyze_tool_requirements(context)

            # Log routing decision
            if requirements.get("mcp_server_hints"):
                log_decision(
                    "pre_tool_use",
                    "mcp_server_selection",
                    ",".join(requirements["mcp_server_hints"]),
                    f"Tool '{context['tool_name']}' requires capabilities: {', '.join(requirements.get('capabilities_needed', []))}",
                )

            # Detect patterns for intelligent routing
            routing_analysis = self._analyze_routing_patterns(context, requirements)

            # Apply learned adaptations
            enhanced_routing = self._apply_routing_adaptations(
                context, routing_analysis
            )

            # Create optimal execution plan
            execution_plan = self._create_execution_plan(context, enhanced_routing)

            # Log execution strategy decision
            log_decision(
                "pre_tool_use",
                "execution_strategy",
                execution_plan["execution_strategy"],
                f"Complexity: {context.get('complexity_score', 0):.2f}, Files: {context.get('file_count', 1)}",
            )

            # Configure tool enhancement
            tool_config = self._configure_tool_enhancement(context, execution_plan)

            # AIDEV-NOTE: Comprehensive Rankle validation moved to PostToolUse
            # Only critical clean code validation happens in main() now
            # Full validation removed - PreToolUse only does critical structural checks

            # Record learning event
            self._record_tool_learning(context, tool_config)

            # Performance validation
            execution_time = (time.time() - start_time) * 1000
            tool_config["performance_metrics"] = {
                "routing_time_ms": execution_time,
                "target_met": execution_time < self.performance_target_ms,
                "efficiency_score": self._calculate_efficiency_score(
                    context, execution_time
                ),
            }

            # Log successful completion
            log_hook_end(
                "pre_tool_use",
                int(execution_time),
                True,
                {
                    "tool_name": context["tool_name"],
                    "mcp_servers": tool_config.get("mcp_integration", {}).get(
                        "servers", []
                    ),
                    "enhanced_mode": tool_config.get("enhanced_mode", False),
                },
            )

            return tool_config

        except Exception as e:
            # Log error
            execution_time = (time.time() - start_time) * 1000
            log_error(
                "pre_tool_use",
                str(e),
                {"tool_name": tool_request.get("tool_name", "unknown")},
            )
            log_hook_end("pre_tool_use", int(execution_time), False)

            # Graceful fallback on error
            return self._create_fallback_tool_config(tool_request, str(e))

    def _extract_tool_context(self, tool_request: dict) -> dict:
        """Extract and enrich tool usage context."""
        # AIDEV-NOTE: Support both real Claude Code schema and legacy test format
        tool_input = tool_request.get("tool_input", tool_request.get("parameters", {}))

        context = {
            "tool_name": tool_request.get("tool_name", ""),
            "tool_parameters": tool_input,  # Real Claude Code uses 'tool_input'
            "session_id": tool_request.get("session_id", ""),
            "transcript_path": tool_request.get("transcript_path", ""),
            "cwd": tool_request.get("cwd", ""),
            "hook_event_name": tool_request.get("hook_event_name", "PreToolUse"),
            "user_intent": tool_request.get("user_intent", ""),
            "session_context": tool_request.get("session_context", {}),
            "previous_tools": tool_request.get("previous_tools", []),
            "operation_sequence": tool_request.get("operation_sequence", []),
            "resource_state": tool_request.get("resource_state", {}),
            "timestamp": time.time(),
        }

        # Extract operation characteristics
        context.update(self._analyze_operation_characteristics(context))

        # Analyze tool chain context
        context.update(self._analyze_tool_chain_context(context))

        return context

    def _analyze_operation_characteristics(self, context: dict) -> dict:
        """Analyze operation characteristics for routing decisions."""
        characteristics = {
            "operation_type": "read",  # AIDEV-NOTE: Simplified without OperationType enum
            "complexity_score": 0.0,
            "file_count": 1,
            "directory_count": 1,
            "parallelizable": False,
            "resource_intensive": False,
            "requires_intelligence": False,
        }

        tool_name = context["tool_name"]
        tool_params = context["tool_parameters"]

        # Determine operation type from tool
        # AIDEV-NOTE: Support both native and MCP Morphllm/Serena file modification tools
        is_write_tool = tool_name in [
            "Write",
            "Edit",
            "MultiEdit",
            "mcp__serena__replace_symbol_body",
            "mcp__serena__insert_after_symbol",
            "mcp__serena__insert_before_symbol"
        ] or tool_name.startswith(("mcp__morphllm-fast-apply__", "mcp__serena__"))

        if is_write_tool:
            characteristics["operation_type"] = "write"
            characteristics["complexity_score"] += 0.2
        elif tool_name in ["Build", "Implement"]:
            characteristics["operation_type"] = "build"
            characteristics["complexity_score"] += 0.4
        elif tool_name in ["Test", "Validate"]:
            characteristics["operation_type"] = "test"
            characteristics["complexity_score"] += 0.1
        elif tool_name in ["Analyze", "Debug"]:
            characteristics["operation_type"] = "analyze"
            characteristics["complexity_score"] += 0.3
            characteristics["requires_intelligence"] = True

        # Analyze file/directory scope
        if "file_path" in tool_params:
            characteristics["file_count"] = 1
        elif "files" in tool_params:
            file_list = tool_params["files"]
            characteristics["file_count"] = (
                len(file_list) if isinstance(file_list, list) else 1
            )
            if characteristics["file_count"] > 3:
                characteristics["parallelizable"] = True
                characteristics["complexity_score"] += 0.3

        if "directory" in tool_params or "path" in tool_params:
            path_param = tool_params.get("directory") or tool_params.get("path", "")
            if "*" in str(path_param) or "**" in str(path_param):
                characteristics["directory_count"] = 5  # Estimate for glob patterns
                characteristics["complexity_score"] += 0.2
                characteristics["parallelizable"] = True

        # Resource intensity analysis
        if (
            characteristics["file_count"] > 10
            or characteristics["complexity_score"] > 0.6
        ):
            characteristics["resource_intensive"] = True

        # Intelligence requirements
        intelligence_tools = ["Analyze", "Debug", "Optimize", "Refactor", "Generate"]
        if any(tool in tool_name for tool in intelligence_tools):
            characteristics["requires_intelligence"] = True

        return characteristics

    def _analyze_tool_chain_context(self, context: dict) -> dict:
        """Analyze tool chain context for optimization opportunities."""
        chain_analysis = {
            "chain_length": len(context["previous_tools"]),
            "pattern_detected": None,
            "optimization_opportunity": False,
            "cache_opportunity": False,
        }

        previous_tools = context["previous_tools"]

        if len(previous_tools) >= 2:
            # Detect common patterns
            tool_names = [tool.get("name", "") for tool in previous_tools[-3:]]

            # Read-Edit pattern
            if any("Read" in name for name in tool_names) and any(
                "Edit" in name for name in tool_names
            ):
                chain_analysis["pattern_detected"] = "read_edit_pattern"
                chain_analysis["optimization_opportunity"] = True

            # Multiple file operations
            if sum(1 for name in tool_names if "file" in name.lower()) >= 2:
                chain_analysis["pattern_detected"] = "multi_file_pattern"
                chain_analysis["optimization_opportunity"] = True

            # Analysis chain
            if (
                sum(
                    1
                    for name in tool_names
                    if any(word in name for word in ["Analyze", "Search", "Find"])
                )
                >= 2
            ):
                chain_analysis["pattern_detected"] = "analysis_chain"
                chain_analysis["cache_opportunity"] = True

        return chain_analysis

    def _analyze_tool_requirements(self, context: dict) -> dict:
        """Analyze tool requirements for capability matching."""
        requirements = {
            "capabilities_needed": [],
            "performance_requirements": {},
            "quality_requirements": {},
            "mcp_server_hints": [],
            "native_tool_sufficient": True,
        }

        tool_name = context["tool_name"]
        characteristics = context

        # Determine required capabilities
        if characteristics.get("requires_intelligence"):
            requirements["capabilities_needed"].extend(
                ["analysis", "reasoning", "context_understanding"]
            )
            requirements["native_tool_sufficient"] = False

        if characteristics.get("complexity_score", 0) > 0.6:
            requirements["capabilities_needed"].extend(
                ["complex_reasoning", "systematic_analysis"]
            )
            requirements["mcp_server_hints"].append("sequential")

        if characteristics.get("file_count", 1) > 5:
            requirements["capabilities_needed"].extend(
                ["multi_file_coordination", "semantic_understanding"]
            )
            requirements["mcp_server_hints"].append("serena")

        # UI/component operations
        if any(
            word in context.get("user_intent", "").lower()
            for word in ["component", "ui", "frontend", "design"]
        ):
            requirements["capabilities_needed"].append("ui_generation")
            requirements["mcp_server_hints"].append("magic")

        # Documentation/library operations
        if any(
            word in context.get("user_intent", "").lower()
            for word in ["library", "documentation", "framework", "api"]
        ):
            requirements["capabilities_needed"].append("documentation_access")
            requirements["mcp_server_hints"].append("context7")

        # Testing operations
        if tool_name in ["Test"] or "test" in context.get("user_intent", "").lower():
            requirements["capabilities_needed"].append("testing_automation")
            requirements["mcp_server_hints"].append("playwright")

        # Performance requirements
        if characteristics.get("resource_intensive"):
            requirements["performance_requirements"] = {
                "max_execution_time_ms": 5000,
                "memory_efficiency_required": True,
                "parallel_execution_preferred": True,
            }
        else:
            requirements["performance_requirements"] = {
                "max_execution_time_ms": 2000,
                "response_time_critical": True,
            }

        # Quality requirements
        if context.get("session_context", {}).get("is_production", False):
            requirements["quality_requirements"] = {
                "validation_required": True,
                "error_handling_critical": True,
                "rollback_capability_needed": True,
            }

        return requirements

    def _analyze_routing_patterns(self, context: dict, requirements: dict) -> dict:
        """Analyze patterns for intelligent routing decisions."""
        # Create operation data for pattern detection
        # AIDEV-NOTE: Simplified without OperationType enum - use string values
        operation_type = context.get("operation_type", "read")
        if hasattr(operation_type, "value"):
            operation_type = operation_type.value
        operation_data = {
            "operation_type": operation_type,
            "file_count": context.get("file_count", 1),
            "complexity_score": context.get("complexity_score", 0.0),
            "tool_name": context["tool_name"],
        }

        # AIDEV-NOTE: Simplified routing without pattern detection
        # Basic routing based on operation requirements
        return {
            "pattern_matches": [],
            "recommended_mcp_servers": [],
            "mcp_activation_plan": {},
            "routing_confidence": 0.7,  # Default moderate confidence
            "optimization_opportunities": self._identify_optimization_opportunities(
                context, requirements
            ),
        }

    def _identify_optimization_opportunities(
        self, context: dict, requirements: dict
    ) -> list:
        """Identify optimization opportunities for tool execution."""
        opportunities = []

        # Parallel execution opportunity
        if context.get("parallelizable") and context.get("file_count", 1) > 3:
            opportunities.append(
                {
                    "type": "parallel_execution",
                    "description": "Multi-file operation suitable for parallel processing",
                    "estimated_speedup": min(context.get("file_count", 1) * 0.3, 2.0),
                }
            )

        # Caching opportunity
        if context.get("cache_opportunity"):
            opportunities.append(
                {
                    "type": "result_caching",
                    "description": "Analysis results can be cached for reuse",
                    "estimated_speedup": 1.5,
                }
            )

        # MCP server coordination
        if len(requirements.get("mcp_server_hints", [])) > 1:
            opportunities.append(
                {
                    "type": "mcp_coordination",
                    "description": "Multiple MCP servers can work together",
                    "quality_improvement": 0.2,
                }
            )

        # Intelligence routing
        if not requirements.get("native_tool_sufficient"):
            opportunities.append(
                {
                    "type": "intelligence_routing",
                    "description": "Operation benefits from MCP server intelligence",
                    "quality_improvement": 0.3,
                }
            )

        return opportunities

    def _apply_routing_adaptations(self, context: dict, routing_analysis: dict) -> dict:
        """Apply routing decisions without learning adaptations."""
        # AIDEV-NOTE: Simplified to return base routing without learning
        return {
            "recommended_mcp_servers": routing_analysis["recommended_mcp_servers"],
            "mcp_activation_plan": routing_analysis["mcp_activation_plan"],
            "optimization_opportunities": routing_analysis[
                "optimization_opportunities"
            ],
        }

    def _create_execution_plan(self, context: dict, enhanced_routing: dict) -> dict:
        """Create optimal execution plan for tool usage."""
        plan = {
            "execution_strategy": "direct",
            "mcp_servers_required": enhanced_routing.get("recommended_mcp_servers", []),
            "parallel_execution": False,
            "caching_enabled": False,
            "fallback_strategy": "native_tools",
            "performance_optimizations": [],
            "estimated_execution_time_ms": 500,
        }

        # Determine execution strategy
        if context.get("complexity_score", 0) > 0.6:
            plan["execution_strategy"] = "intelligent_routing"
        elif context.get("file_count", 1) > 5:
            plan["execution_strategy"] = "parallel_coordination"

        # Configure parallel execution
        if context.get("parallelizable") and context.get("file_count", 1) > 3:
            plan["parallel_execution"] = True
            plan["performance_optimizations"].append("parallel_file_processing")
            plan["estimated_execution_time_ms"] = int(
                plan["estimated_execution_time_ms"] * 0.6
            )

        # Configure caching
        if context.get("cache_opportunity"):
            plan["caching_enabled"] = True
            plan["performance_optimizations"].append("result_caching")

        # Configure MCP coordination
        mcp_servers = plan["mcp_servers_required"]
        if len(mcp_servers) > 1:
            # AIDEV-NOTE: MCPActivationPlan is a dataclass, not a dict - access attribute directly
            mcp_plan = enhanced_routing.get("mcp_activation_plan")
            if mcp_plan and hasattr(mcp_plan, "coordination_strategy"):
                plan["coordination_strategy"] = mcp_plan.coordination_strategy
            else:
                plan["coordination_strategy"] = "collaborative"

        # Estimate execution time based on complexity
        base_time = 200
        complexity_multiplier = 1 + context.get("complexity_score", 0.0)
        file_multiplier = 1 + (context.get("file_count", 1) - 1) * 0.1

        plan["estimated_execution_time_ms"] = int(
            base_time * complexity_multiplier * file_multiplier
        )

        return plan

    def _configure_tool_enhancement(self, context: dict, execution_plan: dict) -> dict:
        """Configure tool enhancement based on execution plan."""
        tool_config = {
            "tool_name": context["tool_name"],
            "enhanced_mode": execution_plan["execution_strategy"] != "direct",
            "mcp_integration": {
                "enabled": len(execution_plan["mcp_servers_required"]) > 0,
                "servers": execution_plan["mcp_servers_required"],
                "coordination_strategy": execution_plan.get(
                    "coordination_strategy", "single_server"
                ),
            },
            "performance_optimization": {
                "parallel_execution": execution_plan["parallel_execution"],
                "caching_enabled": execution_plan["caching_enabled"],
                "optimizations": execution_plan["performance_optimizations"],
            },
            "quality_enhancement": {
                "validation_enabled": context.get("session_context", {}).get(
                    "is_production", False
                ),
                "rankle_quality_enabled": self._should_enable_rankle_validation(
                    context
                ),
                "error_recovery": True,
                "context_preservation": True,
            },
            "execution_metadata": {
                "estimated_time_ms": execution_plan["estimated_execution_time_ms"],
                "complexity_score": context.get("complexity_score", 0.0),
                "intelligence_level": self._determine_intelligence_level(context),
            },
        }

        # Add tool-specific enhancements
        tool_config.update(
            self._get_tool_specific_enhancements(context, execution_plan)
        )

        return tool_config

    def _determine_intelligence_level(self, context: dict) -> str:
        """Determine required intelligence level for operation."""
        complexity = context.get("complexity_score", 0.0)

        if complexity >= 0.8:
            return "high"
        if complexity >= 0.5 or context.get("requires_intelligence"):
            return "medium"
        return "low"

    def _get_tool_specific_enhancements(
        self, context: dict, execution_plan: dict
    ) -> dict:
        """Get tool-specific enhancement configurations."""
        tool_name = context["tool_name"]
        enhancements = {}

        # File operation enhancements
        if tool_name in ["Read", "Write", "Edit"]:
            enhancements["file_operations"] = {
                "integrity_check": True,
                "backup_on_write": context.get("session_context", {}).get(
                    "is_production", False
                ),
                "encoding_detection": True,
            }

        # Multi-file operation enhancements
        if tool_name in ["MultiEdit", "Batch"] or context.get("file_count", 1) > 3:
            enhancements["multi_file_operations"] = {
                "transaction_mode": True,
                "rollback_capability": True,
                "progress_tracking": True,
            }

        # Analysis operation enhancements
        if tool_name in ["Analyze", "Debug", "Search"]:
            enhancements["analysis_operations"] = {
                "deep_context_analysis": context.get("complexity_score", 0.0) > 0.5,
                "semantic_understanding": "serena"
                in execution_plan["mcp_servers_required"],
                "pattern_recognition": True,
            }

        # Build/Implementation enhancements
        if tool_name in ["Build", "Implement", "Generate"]:
            enhancements["build_operations"] = {
                "framework_integration": "context7"
                in execution_plan["mcp_servers_required"],
                "component_generation": "magic"
                in execution_plan["mcp_servers_required"],
                "quality_validation": True,
            }

        return enhancements

    def _should_enable_rankle_validation(self, context: dict) -> bool:
        """Determine if Rankle quality validation should be enabled."""
        if not RANKLE_QUALITY_AVAILABLE:
            return False

        tool_name = context["tool_name"]
        tool_params = context["tool_parameters"]

        # Only validate file modification operations
        is_file_modification_tool = (
            tool_name in ["Edit","Write", "MultiEdit"]
            or tool_name.startswith(("mcp__morphllm-fast-apply__","mcp__serena__"))
        )

        if not is_file_modification_tool:
            return False

        # Check if we have a Python file path to validate (handle both native and MCP Morphllm formats)
        file_path = tool_params.get("file_path", "") or tool_params.get(  # Native tools
            "path", ""
        )  # MCP Morphllm
        if not file_path or not file_path.endswith(".py"):
            return False

        # Check if this is likely a Rankle project file
        return self._is_rankle_project_file(file_path)

    def _is_rankle_project_file(self, file_path: str) -> bool:
        """Check if this file is part of a Rankle project."""
        try:
            # AIDEV-NOTE: Import locally to avoid circular imports
            from pathlib import Path as FilePath

            path = FilePath(file_path)

            # Look for Rankle project indicators
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
                    except Exception:
                        pass

                # Check for rankle-specific directories
                rankle_dirs = (parent / "src" / "ontology").exists() and (
                    parent / "src" / "ml_pipeline"
                ).exists()
                if rankle_dirs:
                    return True

                # Check for pyproject.toml with rankle info
                pyproject = parent / "pyproject.toml"
                if pyproject.exists():
                    try:
                        content = pyproject.read_text(encoding="utf-8")
                        if "rankle" in content.lower():
                            return True
                    except Exception:
                        pass

            return False
        except Exception:
            return False

    def _validate_rankle_quality_sync(self, context: dict) -> None:
        """Synchronous wrapper for Rankle quality validation."""
        if not RANKLE_QUALITY_AVAILABLE:
            return

        # AIDEV-NOTE: Import locally to avoid overhead
        import asyncio

        # Run async validation in sync context
        try:
            # Get or create event loop
            try:
                loop = asyncio.get_running_loop()
                # Schedule on existing loop instead of creating new one
                future = asyncio.run_coroutine_threadsafe(
                    self._validate_rankle_quality_async(context),
                    loop
                )
                future.result(timeout=1.0)
            except RuntimeError:
                # No running loop - safe to create one
                asyncio.run(self._validate_rankle_quality_async(context))

        except Exception as e:
            # Log error but don't block - validation failure shouldn't break workflow
            error_context = {
                "file_path": context.get("tool_parameters", {}).get("file_path", "")
            }
            log_error("rankle_validation", str(e), error_context)

    async def _validate_rankle_quality_async(self, context: dict) -> None:
        """Perform async Rankle quality validation for Python files."""
        if not RANKLE_QUALITY_AVAILABLE:
            return

        tool_params = context["tool_parameters"]
        file_path = tool_params.get("file_path", "")

        if not file_path or not file_path.endswith(".py"):
            return

        try:
            # AIDEV-NOTE: High-performance validation with <100ms target
            start_time = time.time()

            # Get validation engine and cache
            if get_validation_cache is not None:
                get_validation_cache()  # Initialize cache but don't store unused reference
            engine = AsyncValidatorEngine()

            # Extract the actual content that will be written
            content_to_validate = self._extract_content_for_validation(context)
            if not content_to_validate:
                return  # No content to validate

            # Create validation request
            request = ValidationRequest(
                content=content_to_validate,
                file_path=file_path,
                scope=ValidationScope.FULL_FILE,
            )

            # Validate with caching
            result = await engine.validate_request(request)

            # AIDEV-NOTE: ZERO TOLERANCE - block on any violations
            if result.has_violations:
                execution_time = (time.time() - start_time) * 1000
                self._report_rankle_violations_and_block(
                    result, file_path, execution_time
                )

        except Exception as e:
            # Log error but don't block - validation failure shouldn't break workflow
            log_error("rankle_validation", str(e), {"file_path": file_path})

    def _report_rankle_violations_and_block(
        self, result, file_path: str, execution_time_ms: float
    ) -> None:
        """Report Rankle quality violations using spec-compliant response."""
        # Create detailed error message for Claude
        error_message = "\n🚨 RANKLE QUALITY VIOLATIONS DETECTED 🚨\n"
        error_message += f"File: {file_path}\n"
        error_message += (
            f"Total violations: {result.total_violations} (ALL BLOCKING)\n\n"
        )

        # Show Clean Code violations
        if result.clean_code_violations:
            violation_count = len(result.clean_code_violations)
            error_message += f"🚫 Clean Code Violations ({violation_count}):\n"
            for i, violation in enumerate(result.clean_code_violations):
                error_message += (
                    f"  {i + 1}. Line {violation.line}: {violation.message}\n"
                )
                error_message += f"     Rule: {violation.rule}\n"
                error_message += f"     Fix: {violation.fix_instruction}\n\n"

        # Show toolchain violations
        if result.toolchain_violations:
            toolchain_count = len(result.toolchain_violations)
            error_message += f"🔧 Quality Toolchain Violations ({toolchain_count}):\n"
            for i, violation in enumerate(result.toolchain_violations):
                error_message += f"  {i + 1}. {violation}\n"

        error_message += "⚠️  OPERATION BLOCKED - VIOLATIONS MUST BE FIXED!\n"
        error_message += "📋 REQUIRED ACTION:\n"
        error_message += "   1. Fix all violations listed above\n"
        error_message += "   2. Rankle enforces ZERO TOLERANCE for quality violations\n"
        error_message += "   3. All violations must be resolved before continuing\n"

        # Performance info
        if execution_time_ms > 100:
            error_message += (
                f"\n⏱️ Validation: {execution_time_ms:.1f}ms (target: <100ms)\n"
            )
        else:
            error_message += f"\n⏱️ Validation: {execution_time_ms:.1f}ms ✅\n"

        # Use spec-compliant deny response
        response = PreToolUseResponse.deny(
            reason=error_message,
            system_message="🚨 Operation blocked due to Rankle quality violations"
        )
        response.output_and_exit(exit_code=0)

    def _calculate_efficiency_score(
        self, context: dict, execution_time_ms: float
    ) -> float:
        """Calculate efficiency score for the routing decision."""
        # Base efficiency is inverse of execution time relative to target
        time_efficiency = min(
            self.performance_target_ms / max(execution_time_ms, 1), 1.0
        )

        # Complexity handling efficiency
        complexity = context.get("complexity_score", 0.0)
        complexity_efficiency = 1.0 - (complexity * 0.3)  # Some complexity is expected

        # Resource utilization efficiency
        resource_usage = context.get("resource_state", {}).get("usage_percent", 0)
        resource_efficiency = 1.0 - max(resource_usage - 70, 0) / 100.0

        # Weighted efficiency score
        efficiency_score = (
            time_efficiency * 0.4
            + complexity_efficiency * 0.3
            + resource_efficiency * 0.3
        )

        return max(min(efficiency_score, 1.0), 0.0)

    def _record_tool_learning(self, context: dict, tool_config: dict):
        """Record tool usage for learning purposes (disabled)."""
        # AIDEV-NOTE: Learning engine removed - this is now a no-op
        pass

    def _create_fallback_tool_config(self, tool_request: dict, error: str) -> dict:
        """Create fallback tool configuration on error."""
        return {
            "tool_name": tool_request.get("tool_name", "unknown"),
            "enhanced_mode": False,
            "fallback_mode": True,
            "error": error,
            "mcp_integration": {
                "enabled": False,
                "servers": [],
                "coordination_strategy": "none",
            },
            "performance_optimization": {
                "parallel_execution": False,
                "caching_enabled": False,
                "optimizations": [],
            },
            "performance_metrics": {
                "routing_time_ms": 0,
                "target_met": False,
                "error_occurred": True,
            },
        }

    def _extract_content_for_validation(self, context: dict) -> str:
        """Extract the content that will be written/edited for validation."""
        tool_name = context["tool_name"]
        tool_params = context["tool_parameters"]

        try:
            # AIDEV-NOTE: Fixed syntax - startswith requires tuple for multiple prefixes
            if tool_name == "Write" or tool_name.startswith((
                "mcp__morphllm-fast-apply__write",
                "mcp__serena__replace_symbol_body",
                "mcp__serena__insert_after_symbol",
                "mcp__serena__insert_before_symbol"
            )):
                # For Write operations, validate the full content being written
                return tool_params.get("content", tool_params.get("body", ""))

            if tool_name == "Edit" or tool_name.startswith((
                "mcp__morphllm-fast-apply__edit",
                "mcp__serena__replace_symbol_body",
                "mcp__serena__insert_after_symbol",
                "mcp__serena__insert_before_symbol"
            )):
                # For Edit operations, apply the edit and validate the result
                file_path = (
                    tool_params.get("file_path") or tool_params.get("path") or ""
                )
                code_edit = tool_params.get("code_edit")
                old_string = tool_params.get("old_string", "")
                new_string = tool_params.get("new_string", "")

                # Read current file content
                from pathlib import Path

                if not file_path or not Path(file_path).exists():
                    return ""
                current_content = Path(file_path).read_text(encoding="utf-8")
                if tool_name == "Edit":
                    # Apply the edit
                    if old_string and old_string in current_content:
                        return current_content.replace(
                            old_string, new_string, 1
                        )  # Replace only first occurrence
                    return ""  # If old_string not found, can't predict the result - skip validation

                # mcp__morphllm-fast-apply__edit_file
                if not code_edit:
                    return ""  # Required for this tool; skip prediction of missing
                return ""  # Default: skip predicting code_edit pre-exec

            # AIDEV-NOTE: Fixed syntax - startswith requires tuple for multiple prefixes
            if tool_name == "MultiEdit" or tool_name.startswith((
                "mcp__morphllm-fast-apply__multi",
                "mcp__serena__replace_symbol_body",
                "mcp__serena__insert_after_symbol",
                "mcp__serena__insert_before_symbol"
            )):
                # For MultiEdit operations, apply all edits and validate the result
                file_path = tool_params.get("file_path", "")
                edits = tool_params.get("edits", [])

                # Read current file content
                from pathlib import Path

                if Path(file_path).exists():
                    current_content = Path(file_path).read_text(encoding="utf-8")
                    modified_content = current_content

                    # Apply all edits sequentially
                    for edit in edits:
                        old_string = edit.get("old_string", "")
                        new_string = edit.get("new_string", "")
                        if old_string in modified_content:
                            modified_content = modified_content.replace(
                                old_string, new_string, 1
                            )  # Replace only first occurrence
                        else:
                            # If any edit fails, can't predict result - skip validation
                            return ""

                    return modified_content
                # File doesn't exist, can't predict edit result
                return ""

            # Unknown tool type, no content to validate
            return ""

        except Exception as e:
            # If content extraction fails, log error but don't block
            log_error(
                "content_extraction",
                str(e),
                {"tool_name": tool_name, "file_path": tool_params.get("file_path", "")},
            )
            return ""


def _validate_rankle_quality_early(tool_request: dict) -> None:
    """
    Perform Rankle quality validation EARLY before any other processing.
    This follows the user's example pattern of validating at the start of main().
    """
    try:
        # Extract tool context
        tool_name = tool_request.get("tool_name", "")
        tool_input = tool_request.get("tool_input", tool_request.get("parameters", {}))

        # Only validate file modification operations for Python files
        is_file_modification_tool = tool_name in ([
            "Edit",
            "Write",
            "MultiEdit",
        ] or tool_name.startswith(("mcp__morphllm-fast-apply__", "mcp__serena__"))
        
        )

        if not is_file_modification_tool:
            return

        file_path = tool_input.get("file_path", "")
        if not file_path or not file_path.endswith(".py"):
            return

        # Check if this is a Rankle project file
        if not _is_rankle_project_file_simple(file_path):
            return

        # Extract content to validate
        content_to_validate = _extract_content_for_validation_simple(
            tool_name, tool_input, file_path
        )
        if not content_to_validate.strip():
            return

        # Run validation
        import asyncio
        import time

        start_time = time.time()

        # Create validation request
        validation_request = ValidationRequest(
            file_path=file_path,
            content=content_to_validate,
            scope=ValidationScope.FULL_FILE,
        )

        # Run async validation
        try:
            loop = asyncio.get_running_loop()
            # Schedule on existing loop
            future = asyncio.run_coroutine_threadsafe(
                _run_validation_async(validation_request),
                loop
            )
            result = future.result(timeout=5.0)
        except RuntimeError:    
            # No running loop - safe to create one
            result = asyncio.run(_run_validation_async(validation_request))

        execution_time_ms = (time.time() - start_time) * 1000

        # Check for violations and block if found
        if result and result.total_violations > 0:
            _report_violations_and_exit(result, file_path, execution_time_ms)

    except Exception as e:
        # Log error but don't block operation for validation errors
        # Note: Errors are logged but don't affect the hook response
        pass


async def _run_validation_async(validation_request: ValidationRequest):
    """Run async validation."""
    engine = AsyncValidatorEngine()
    return await engine.validate_request(validation_request)


def _is_rankle_project_file_simple(file_path: str) -> bool:
    """Simple Rankle project detection without full hook dependencies."""
    try:
        from pathlib import Path

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
                except Exception:
                    pass

            # Check for rankle-specific directories
            if (parent / "src" / "ontology").exists() and (
                parent / "src" / "ml_pipeline"
            ).exists():
                return True
        return False
    except Exception:
        return False


def _extract_content_for_validation_simple(
    tool_name: str, tool_input: dict, file_path: str
) -> str:
    """Simple content extraction for validation."""
    try:
        if tool_name == "Write" or tool_name.startswith((
            "mcp__morphllm-fast-apply__write",
            "mcp__serena__replace_symbol_body",
            "mcp__serena__insert_after_symbol",
            "mcp__serena__insert_before_symbol"
        )):
            return tool_input.get("content", "")
        if tool_name == "Edit" or tool_name.startswith(
            "mcp__morphllm-fast-apply__edit"
        ):
            # For Edit, we need to apply the edit to get the final content
            old_string = tool_input.get("old_string", "")
            new_string = tool_input.get("new_string", "")

            # Read current file content
            try:
                with open(file_path, encoding="utf-8") as f:
                    current_content = f.read()
            except Exception:
                current_content = ""

            # Apply edit
            if old_string and old_string in current_content:
                return current_content.replace(old_string, new_string, 1)
            return current_content + "\n" + new_string
        if tool_name == "MultiEdit" or tool_name.startswith(
            "mcp__morphllm-fast-apply__multi"
        ):
            # For MultiEdit, apply all edits sequentially
            edits = tool_input.get("edits", [])
            if not edits:
                return ""

            # Read current file content
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                content = ""

            # Apply edits in sequence
            for edit in edits:
                old_str = edit.get("old_string", "")
                new_str = edit.get("new_string", "")
                if old_str and old_str in content:
                    content = content.replace(old_str, new_str, 1)

            return content
        return ""
    except Exception:
        return ""


def _report_violations_and_exit(
    result, file_path: str, execution_time_ms: float
) -> None:
    """Report violations and block operation using spec-compliant response."""
    error_message = "\n🚨 RANKLE QUALITY VIOLATIONS DETECTED (PreToolUse) 🚨\n"
    error_message += f"File: {file_path}\n"
    error_message += f"Total violations: {result.total_violations} (ALL BLOCKING)\n\n"

    # Show Clean Code violations
    if result.clean_code_violations:
        error_message += (
            f"🚫 Clean Code Violations ({len(result.clean_code_violations)}):\n"
        )
        for i, violation in enumerate(result.clean_code_violations):
            error_message += f"  {i + 1}. Line {violation.line}: {violation.message}\n"
            error_message += f"     Rule: {violation.rule}\n"
            if hasattr(violation, "fix_instruction"):
                error_message += f"     Fix: {violation.fix_instruction}\n\n"

    # Show toolchain violations
    if result.toolchain_violations:
        error_message += (
            f"🔧 Quality Toolchain Violations ({len(result.toolchain_violations)}):\n"
        )
        for i, violation in enumerate(result.toolchain_violations):
            error_message += f"  {i + 1}. {violation}\n"

    error_message += "⚠️  OPERATION BLOCKED BY PRE-TOOL VALIDATION!\n"
    error_message += "📋 REQUIRED ACTION:\n"
    error_message += "   1. Fix all violations listed above\n"
    error_message += "   2. Rankle enforces ZERO TOLERANCE for quality violations\n"
    error_message += "   3. Operation will not proceed until violations are resolved\n"

    # Performance info
    if execution_time_ms > 100:
        error_message += f"\n⏱️ Validation: {execution_time_ms:.1f}ms (target: <100ms)\n"
    else:
        error_message += f"\n⏱️ Validation: {execution_time_ms:.1f}ms ✅\n"

    # Use spec-compliant deny response
    response = PreToolUseResponse.deny(
        reason=error_message,
        system_message="🚨 Operation blocked due to quality violations"
    )
    response.output_and_exit(exit_code=0)


def _is_rankle_project_file(file_path: str) -> bool:
    """Check if this file is part of a Rankle project."""
    path = Path(file_path)

    # Look for Rankle project indicators
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
            except Exception:
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
            except Exception:
                pass

    return False


def _validate_critical_clean_code_only(tool_request: dict[str, Any]) -> None:
    """
    PreToolUse validation - ONLY critical clean code issues that prevent tools from running.

    Blocks only:
    - Line length violations (>88 chars)
    - Missing AIDEV-NOTE anchors for complex code
    - Magic numbers (non-0,1,-1 literals)
    - File length violations (>600 lines)
    - Function length violations (>50 lines)
    - Nesting depth violations (>4 levels)
    - Cyclomatic complexity violations (>10)
    - Naming convention violations (snake_case, CamelCase, SCREAMING_SNAKE_CASE)

    Does NOT block:
    - Formatting issues (black can fix)
    - Import sorting (isort can fix)
    - Whitespace/indentation (black can fix)
    - Trailing commas (black can fix)
    - Quote style (black can fix)
    """
    tool_name = tool_request.get("tool_name", "")
    tool_params = tool_request.get(
        "tool_input", tool_request.get("tool_parameters", {})
    )

    # Only validate file modification operations
    # AIDEV-NOTE: Fixed syntax - startswith requires tuple for multiple prefixes
    is_file_modification_tool = tool_name in [
        "Edit",
        "Write",
        "MultiEdit",
    ] or tool_name.startswith(("mcp__morphllm-fast-apply__", "mcp__serena__"))

    if not is_file_modification_tool:
        return

    # Extract file path (handle both native and MCP Morphllm formats)
    file_path = tool_params.get("file_path", "") or tool_params.get(  # Native tools
        "path", ""
    )  # MCP Morphllm
    if not file_path or not file_path.endswith(".py"):
        return

    # AIDEV-NOTE: Skip validation for hook files to prevent circular dependency/infinite loop
    # Handles both production (.claude/hooks/) and development (hooks/) paths
    if "/.claude/hooks/" in file_path or "/hooks/" in file_path or file_path.startswith("hooks/"):
        return

    # AIDEV-NOTE: Validate ANY .py file, not just Rankle project files
    # Removed project file restriction - hooks should work for any Python file

    try:
        from rankle_quality_validators import RankleQualityValidator

        # Get content to validate - either new content or existing file content
        if tool_name == "Write":
            # For Write operations, validate the content being written
            file_content = tool_params.get("content", "")
        elif tool_name == "Edit":
            # For Edit operations, apply the edit and validate the result
            if not Path(file_path).exists():
                return  # Skip validation if editing non-existent file
            current_content = Path(file_path).read_text(encoding="utf-8")
            old_string = tool_params.get("old_string", "")
            new_string = tool_params.get("new_string", "")
            if old_string and old_string in current_content:
                file_content = current_content.replace(old_string, new_string, 1)
            else:
                return  # Can't predict result if old_string not found
        elif tool_name == "MultiEdit":
            # For MultiEdit operations, apply all edits and validate the result
            if not Path(file_path).exists():
                return  # Skip validation if editing non-existent file
            current_content = Path(file_path).read_text(encoding="utf-8")
            file_content = current_content
            edits = tool_params.get("edits", [])
            for edit in edits:
                old_string = edit.get("old_string", "")
                new_string = edit.get("new_string", "")
                if old_string and old_string in file_content:
                    file_content = file_content.replace(old_string, new_string, 1)
                else:
                    return  # Can't predict result if any edit fails
        # AIDEV-NOTE: Fixed syntax - startswith requires tuple for multiple prefixes
        elif tool_name.startswith(("mcp__morphllm-fast-apply__", "mcp__serena__")):
            # Handle MCP Morphllm and Serena tools - they use 'path'/'relative_path' instead of 'file_path'
            mcp_file_path = tool_params.get(
                "path", tool_params.get("relative_path", file_path)
            )  # Fallback to file_path if neither found

            # AIDEV-NOTE: Fixed syntax - use 'in' for membership test, not '=='
            if tool_name in (
                "mcp__morphllm-fast-apply__write_file",
                "mcp__serena__replace_symbol_body",
                "mcp__serena__insert_after_symbol",
                "mcp__serena__insert_before_symbol"
                ):
                # Write operation
                file_content = tool_params.get("content", tool_params.get("body", ""))
            elif tool_name in (
                "mcp__morphllm-fast-apply__edit_file",
                "mcp__serena__replace_symbol_body",
                "mcp__serena__insert_after_symbol",
                "mcp__serena__insert_before_symbol"
                ):
                # Edit operation with code_edit parameter
                if not Path(mcp_file_path).exists():
                    return  # Skip validation if editing non-existent file
                current_content = Path(mcp_file_path).read_text(encoding="utf-8")
                # For code_edit, we can't predict the result, so use current content as baseline
                file_content = current_content
            elif tool_name in (
                "mcp__morphllm-fast-apply__tiny_edit_file",
                "mcp__serena__replace_symbol_body",
                "mcp__serena__insert_after_symbol",
                "mcp__serena__insert_before_symbol"
                ):
                # Tiny edit with edits array
                if not Path(mcp_file_path).exists():
                    return  # Skip validation if editing non-existent file
                current_content = Path(mcp_file_path).read_text(encoding="utf-8")
                file_content = current_content
                edits = tool_params.get("edits", [])
                for edit in edits:
                    old_text = edit.get("oldText", "")
                    new_text = edit.get("newText", "")
                    if old_text and old_text in file_content:
                        file_content = file_content.replace(old_text, new_text, 1)
                    else:
                        return  # Can't predict result if any edit fails
            else:
                return  # Unknown MCP Morphllm operation
        else:
            return  # Unknown tool type

        # Use RankleQualityValidator with proper project root detection
        from project_utils import get_project_root_from_file

        # Detect project root from the file being validated
        project_root = get_project_root_from_file(file_path)
        project_root_str = str(project_root) if project_root else ""

        validator = RankleQualityValidator(project_root=project_root_str)
        violations = validator.validate_content(file_content, file_path)

        # AIDEV-NOTE: BLOCKS tool execution on ANY quality violation - prevents agent drift
        # Block if ANY violations found (all Rankle violations are critical structural issues)
        if violations:
            _report_critical_violations_and_block(violations, file_path)

    except Exception as e:
        # If validation system fails, allow operation (fail-safe)
        # Note: We don't output here, main() will handle the response
        return


def _report_critical_violations_and_block(violations: list, file_path: str) -> None:
    """Report critical clean code violations using spec-compliant response."""
    error_message = "\n🚨 CRITICAL CLEAN CODE VIOLATIONS 🚨\n"
    error_message += f"File: {file_path}\n"
    error_message += f"Critical violations: {len(violations)} (ALL BLOCKING)\n\n"

    error_message += "🚫 Critical Issues (BLOCKING):\n"
    for i, violation in enumerate(violations[:10]):  # Show first 10 to avoid spam
        error_message += f"  {i + 1}. Line {violation.line}: {violation.message}\n"
        error_message += f"     Rule: {violation.rule}\n"
        error_message += f"     Fix: {violation.fix_instruction}\n\n"

    if len(violations) > 10:
        error_message += f"  ... and {len(violations) - 10} more violations\n\n"

    error_message += (
        "⚠️  OPERATION BLOCKED: Fix critical structural issues before proceeding\n"
    )
    error_message += "📋 These prevent tools from working properly:\n"
    error_message += "   • Line length, function/file size, nesting depth\n"
    error_message += "   • Magic numbers, naming conventions, complexity\n"
    error_message += (
        "🔧 Formatting/linting errors will be validated AFTER tool execution\n"
    )

    # Use spec-compliant deny response
    response = PreToolUseResponse.deny(
        reason=error_message,
        system_message="🚨 Operation blocked due to critical code quality issues"
    )
    response.output_and_exit(exit_code=0)


def main():
    """Main hook execution function with advanced features."""
    try:
        # Read tool request from stdin
        tool_request = json.loads(sys.stdin.read())

        # Extract tool info
        tool_name = tool_request.get("tool_name", "")
        tool_input = tool_request.get("tool_input", {})
        cwd = tool_request.get("cwd", os.getcwd())

        # ADVANCED FEATURE 1: Path Normalization with updatedInput
        path_normalizer = PathNormalizer(cwd)
        updated_input, path_modified = path_normalizer.fix_tool_input_paths(tool_name, tool_input)

        # ADVANCED FEATURE 2: Destructive Operation Detection with ask
        # Set ask_for_confirmation=True to enable (disabled by default for now)
        destructor_detector = DestructiveOperationDetector(ask_for_confirmation=False)
        should_ask, ask_reason = destructor_detector.should_ask_confirmation(tool_name, tool_input)

        if should_ask:
            # Use permissionDecision: "ask" to request user confirmation
            response = PreToolUseResponse.ask(
                reason=ask_reason,
                system_message="⚠️ Confirmation required for destructive operation"
            )
            response.output_and_exit(exit_code=0)

        # PreToolUse validates critical clean code issues before tool execution
        # Linting and formatting validation moved to PostToolUse where tools can fix them
        _validate_critical_clean_code_only(tool_request)

        # Initialize and run hook
        hook = PreToolUseHook()
        result = hook.process_tool_use(tool_request)

        # Return spec-compliant allow response
        # If path was modified, include updatedInput
        if path_modified:
            response = PreToolUseResponse.allow(
                reason="Tool validated and ready for execution",
                updated_input=updated_input,
                system_message=f"✓ Path normalized | SuperClaude intelligence applied"
            )
        else:
            response = PreToolUseResponse.allow(
                reason="Tool validated and ready for execution",
                system_message=f"SuperClaude-Lite intelligence applied"
            )
        response.output_and_exit(exit_code=0)

    except Exception as e:
        # ADVANCED FEATURE 3: Critical Error Detection with continue: false
        error_detector = CriticalErrorDetector()
        is_critical, critical_reason = error_detector.is_critical_error(e)

        if is_critical:
            # Stop processing on critical errors
            response = PreToolUseResponse.deny(
                reason=critical_reason,
                continue_execution=False,  # Stop all hook processing
                system_message="🚨 Critical error - hook processing stopped"
            )
            response.output_and_exit(exit_code=0)
        else:
            # Non-critical errors: fail-safe mode (allow operation)
            error_message = f"Hook error: {str(e)}"
            response = PreToolUseResponse.allow(
                reason=error_message,
                system_message="⚠️ Hook error (operation allowed in fail-safe mode)"
            )
            response.output_and_exit(exit_code=0)

class RankleQualityPreToolUseHook(PreToolUseHook):
    """Backward-compatible alias for older imports."""
    pass

if __name__ == "__main__":
    main()
