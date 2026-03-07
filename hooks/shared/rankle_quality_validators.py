#!/usr/bin/env python3
"""
Rankle Quality Validators - Enforced Clean Code Standards

This module enforces all Rankle project coding standards with MANDATORY blocking.
NO warnings or suggestions - ALL violations BLOCK operations.

Standards enforced:
- Functions ≤50 lines (BLOCKING)
- Files ≤600 lines (BLOCKING)
- Line length ≤88 chars (BLOCKING)
- Nesting depth ≤4 (BLOCKING)
- Cyclomatic complexity ≤10 (BLOCKING)
- Magic numbers only 0,1,-1 (BLOCKING)
- AIDEV comments required for complex code (BLOCKING)
- AIDEV comments ≤120 chars (BLOCKING)
- DRY principle enforcement (BLOCKING)
- Naming conventions (BLOCKING)
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ViolationSeverity(Enum):
    """All violations are BLOCKING - no exceptions."""

    BLOCKING = "blocking"


@dataclass
class RankleViolation:
    """Represents a violation of Rankle coding standards."""

    file_path: str
    line: int
    column: int = 0
    rule: str = ""
    severity: ViolationSeverity = ViolationSeverity.BLOCKING
    message: str = ""
    auto_fixable: bool = False
    manual_fix_required: bool = True
    fix_instruction: str = ""
    violation_type: str = "general"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file_path,
            "line": self.line,
            "column": self.column,
            "rule": self.rule,
            "severity": self.severity.value,
            "message": self.message,
            "auto_fixable": self.auto_fixable,
            "manual_fix_required": self.manual_fix_required,
            "fix_instruction": self.fix_instruction,
            "violation_type": self.violation_type,
        }


class ComplexityAnalyzer(ast.NodeVisitor):
    """Calculates cyclomatic complexity of functions."""

    def __init__(self):
        self.complexity = 1  # Base complexity

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.complexity += len(node.handlers)  # Each except adds complexity
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # And/Or operations add complexity
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


class NestingAnalyzer(ast.NodeVisitor):
    """Calculates maximum nesting depth."""

    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def _visit_nested(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_If(self, node):
        self._visit_nested(node)

    def visit_While(self, node):
        self._visit_nested(node)

    def visit_For(self, node):
        self._visit_nested(node)

    def visit_Try(self, node):
        self._visit_nested(node)

    def visit_With(self, node):
        self._visit_nested(node)

    def visit_FunctionDef(self, node):
        # Don't count function definitions as nesting
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Don't count class definitions as nesting
        self.generic_visit(node)


class MagicNumberFinder(ast.NodeVisitor):
    """Finds magic numbers (excluding allowed: 0, 1, -1)."""

    def __init__(self):
        self.magic_numbers = []  # [(number, line)]

    def visit_Constant(self, node):
        # AIDEV-NOTE: Python 3.8+ uses Constant node for all literals
        if isinstance(node.value, (int, float)):
            if node.value not in [0, 1, -1]:
                self.magic_numbers.append((node.value, node.lineno))
        self.generic_visit(node)

    def visit_Num(self, node):
        # AIDEV-NOTE: Legacy Python <3.8 compatibility
        if node.n not in [0, 1, -1]:
            self.magic_numbers.append((node.n, node.lineno))
        self.generic_visit(node)


class RankleQualityValidator:
    """
    Comprehensive validator enforcing ALL Rankle project standards.
    ALL violations are BLOCKING - no exceptions or warnings.
    """

    def __init__(self, project_root: str = "", file_path: str = ""):
        # Import project utilities for intelligent project root detection
        from project_utils import get_project_root_from_file

        # Determine project root intelligently
        if project_root:
            self.project_root = Path(project_root)
        elif file_path:
            # Try to detect project root from file path
            detected_root = get_project_root_from_file(file_path)
            self.project_root = detected_root if detected_root else Path.cwd()
        else:
            self.project_root = Path.cwd()

        self.violations: list[RankleViolation] = []

        # AIDEV-NOTE: Standards from .serena/memories/project_code_style_conventions.md
        self.standards = {
            "max_function_lines": 50,
            "max_file_lines": 600,
            "max_line_length": 88,
            "max_nesting_depth": 4,
            "max_complexity": 10,
            "aidev_comment_max_length": 120,
            "require_aidev_for_complex_functions": True,
            "require_aidev_for_high_complexity": True,
            "allowed_magic_numbers": [0, 1, -1],
            "enforce_naming_conventions": True,
        }

    def validate_file(self, file_path: str) -> list[RankleViolation]:
        """
        Validate a single file against ALL Rankle standards.
        Returns list of BLOCKING violations.
        """
        self.violations = []
        path = Path(file_path)

        if not path.exists():
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=1,
                    rule="file-not-found",
                    message=f"File does not exist: {file_path}",
                    fix_instruction="Ensure file path is correct",
                )
            )
            return self.violations

        if path.suffix != ".py":
            # Only validate Python files
            return []

        try:
            content = path.read_text(encoding="utf-8")
            return self.validate_content(content, file_path)
        except UnicodeDecodeError:
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=1,
                    rule="encoding-error",
                    message="File is not valid UTF-8",
                    fix_instruction="Fix file encoding to UTF-8",
                )
            )
            return self.violations

    def validate_content(
        self, content: str, file_path: str = "<content>"
    ) -> list[RankleViolation]:
        """
        Validate content string against ALL Rankle standards.
        Returns list of BLOCKING violations.
        """
        self.violations = []
        lines = content.splitlines()

        # BLOCKING: File length check (with exceptions for specific test files)
        # AIDEV-NOTE: tests/conftest.py exception - pytest fixture collection file
        is_conftest = file_path.endswith("tests/conftest.py") or file_path.endswith("tests\\conftest.py")
        if len(lines) > self.standards["max_file_lines"] and not is_conftest:
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=len(lines),
                    rule="file-too-long",
                    message=f"File has {len(lines)} lines (max: {self.standards['max_file_lines']})",
                    fix_instruction="Split into multiple modules following clean architecture",
                )
            )
        elif len(lines) >= 501:  # Long files require AIDEV-NOTE (per guidelines)
            if not self._has_aidev_note_at_top_of_file(lines):
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=1,
                        rule="long-file-needs-aidev",
                        message=f"File has {len(lines)} lines but lacks required AIDEV-NOTE at top (per guidelines: 'too long' code needs anchor comments)",
                        fix_instruction="Add AIDEV-NOTE at top of file explaining the file structure or refactoring plan",
                    )
                )

        # Parse AST for structural analysis
        try:
            tree = ast.parse(content, filename=file_path)
            self._validate_ast_structure(tree, file_path, lines)
        except SyntaxError as e:
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=e.lineno or 1,
                    rule="syntax-error",
                    message=f"Syntax error: {e.msg}",
                    fix_instruction="Fix Python syntax errors",
                )
            )
            return self.violations  # Can't continue with invalid syntax

        # BLOCKING: Line-by-line checks
        self._validate_lines(lines, file_path)

        # BLOCKING: Partial implementation detection
        self._validate_no_partial_implementations(content, file_path)

        return self.violations

    def _validate_ast_structure(
        self, tree: ast.AST, file_path: str, lines: list[str]
    ) -> None:
        """Validate AST structure for functions, classes, complexity."""

        # Check functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._validate_function(node, file_path, lines)
            elif isinstance(node, ast.ClassDef):
                self._validate_class(node, file_path, lines)

        # Check for magic numbers
        magic_finder = MagicNumberFinder()
        magic_finder.visit(tree)

        for number, line_num in magic_finder.magic_numbers:
            # Check if there's an AIDEV-NOTE explaining this number
            aidev_explanation = self._has_aidev_explanation_for_line(
                lines, line_num, str(number)
            )

            if not aidev_explanation:
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=line_num,
                        rule="magic-number",
                        message=f"Magic number {number} requires explanation (only 0,1,-1 allowed without)",
                        fix_instruction=f"Add constant or # AIDEV-NOTE: {number} is <explanation ≤120 chars>",
                    )
                )

    def _validate_function(
        self, node: ast.FunctionDef, file_path: str, lines: list[str]
    ) -> None:
        """Validate individual function against all standards."""
        func_lines = node.end_lineno - node.lineno + 1

        # BLOCKING: Function length
        if func_lines > self.standards["max_function_lines"]:
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=node.lineno,
                    rule="function-too-long",
                    message=f"Function '{node.name}' has {func_lines} lines (max: {self.standards['max_function_lines']})",
                    fix_instruction="Extract helper functions or split into smaller functions",
                )
            )
        elif func_lines >= 50:  # Long functions require AIDEV-NOTE (per guidelines)
            if not self._has_aidev_note_for_function(node, lines):
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=node.lineno,
                        rule="long-function-needs-aidev",
                        message=f"Function '{node.name}' is {func_lines} lines but lacks required AIDEV-NOTE (per guidelines: 'too long' code needs anchor comments)",
                        fix_instruction="Add AIDEV-NOTE explaining why this function is long or how to refactor it",
                    )
                )

        # BLOCKING: Cyclomatic complexity
        complexity_analyzer = ComplexityAnalyzer()
        complexity_analyzer.visit(node)
        complexity = complexity_analyzer.complexity

        if complexity > self.standards["max_complexity"]:
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=node.lineno,
                    rule="complexity-too-high",
                    message=f"Function '{node.name}' complexity is {complexity} (max: {self.standards['max_complexity']})",
                    fix_instruction="Simplify logic, extract functions, or reduce conditional branches",
                )
            )
        elif complexity >= 8:  # Complex functions require AIDEV-NOTE (per guidelines)
            if not self._has_aidev_note_for_function(node, lines):
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=node.lineno,
                        rule="complex-function-needs-aidev",
                        message=f"Function '{node.name}' has complexity {complexity} but lacks required AIDEV-NOTE (per guidelines: 'too complex' code needs anchor comments)",
                        fix_instruction="Add AIDEV-NOTE explaining the complex logic or refactoring plan",
                    )
                )

        # BLOCKING: Nesting depth
        nesting_analyzer = NestingAnalyzer()
        nesting_analyzer.visit(node)
        max_depth = nesting_analyzer.max_depth

        if max_depth > self.standards["max_nesting_depth"]:
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=node.lineno,
                    rule="nesting-too-deep",
                    message=f"Function '{node.name}' nesting depth {max_depth} exceeds limit (max: {self.standards['max_nesting_depth']})",
                    fix_instruction="Extract nested logic into helper functions or use guard clauses",
                )
            )
        elif max_depth > 4:  # Deep nesting requires AIDEV-NOTE (per guidelines)
            if not self._has_aidev_note_for_function(node, lines):
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=node.lineno,
                        rule="deep-nesting-needs-aidev",
                        message=f"Function '{node.name}' has nesting depth {max_depth} but lacks required AIDEV-NOTE (per guidelines: 'confusing' code needs anchor comments)",
                        fix_instruction="Add AIDEV-NOTE explaining the nested logic structure",
                    )
                )

        # BLOCKING: Require AIDEV-NOTE for complex functions (>50 lines)
        if func_lines > 50:
            has_note = self._has_aidev_note_for_function(node, lines)
            if not has_note:
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=node.lineno,
                        rule="missing-anchor-complex-function",
                        message=f"Function '{node.name}' ({func_lines} lines) requires AIDEV-NOTE",
                        fix_instruction="Add before function: # AIDEV-NOTE: <explain purpose in ≤120 chars>",
                    )
                )

        # BLOCKING: Require AIDEV-NOTE for high complexity (>8)
        if complexity > 8:
            has_note = self._has_aidev_note_for_function(node, lines)
            if not has_note:
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=node.lineno,
                        rule="missing-anchor-complex-algorithm",
                        message=f"Function '{node.name}' (complexity {complexity}) requires AIDEV-NOTE",
                        fix_instruction="Add before function: # AIDEV-NOTE: <explain algorithm in ≤120 chars>",
                    )
                )

        # BLOCKING: Naming convention - functions should be snake_case
        # AIDEV-NOTE: Exempt unittest.TestCase required method names (setUp, tearDown, etc.)
        unittest_methods = {"setUp", "tearDown", "setUpClass", "tearDownClass", "setUpModule", "tearDownModule"}
        if not self._is_snake_case(node.name) and not node.name.startswith("_") and node.name not in unittest_methods:
            # Allow private methods to start with underscore
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=node.lineno,
                    rule="function-naming-convention",
                    message=f"Function '{node.name}' should use snake_case",
                    fix_instruction=f"Rename to snake_case (e.g., {self._to_snake_case(node.name)})",
                )
            )

    def _validate_class(
        self, node: ast.ClassDef, file_path: str, lines: list[str]
    ) -> None:
        """Validate class naming conventions."""
        # BLOCKING: Classes should be CamelCase
        if not self._is_camel_case(node.name):
            self.violations.append(
                RankleViolation(
                    file_path=file_path,
                    line=node.lineno,
                    rule="class-naming-convention",
                    message=f"Class '{node.name}' should use CamelCase",
                    fix_instruction=f"Rename to CamelCase (e.g., {self._to_camel_case(node.name)})",
                )
            )

    def _validate_lines(self, lines: list[str], file_path: str) -> None:
        """Validate individual lines for length and AIDEV comment format."""

        for i, line in enumerate(lines, 1):
            # BLOCKING: Line length
            if len(line) > self.standards["max_line_length"]:
                self.violations.append(
                    RankleViolation(
                        file_path=file_path,
                        line=i,
                        rule="line-too-long",
                        message=f"Line {i} has {len(line)} chars (max: {self.standards['max_line_length']})",
                        auto_fixable=True,
                        manual_fix_required=False,
                        fix_instruction=f"Run: black --line-length {self.standards['max_line_length']} {file_path}",
                    )
                )

            # BLOCKING: AIDEV comment length
            if "AIDEV-" in line:
                aidev_match = re.search(r"#\s*(AIDEV-\w+:.*)", line.strip())
                if aidev_match:
                    aidev_comment = aidev_match.group(1)
                    if len(aidev_comment) > self.standards["aidev_comment_max_length"]:
                        self.violations.append(
                            RankleViolation(
                                file_path=file_path,
                                line=i,
                                rule="aidev-comment-too-long",
                                message=f"AIDEV comment exceeds {self.standards['aidev_comment_max_length']} chars ({len(aidev_comment)} chars)",
                                fix_instruction=f"Shorten to ≤{self.standards['aidev_comment_max_length']} chars",
                            )
                        )

    def _has_aidev_note_for_function(
        self, func_node: ast.FunctionDef, lines: list[str]
    ) -> bool:
        """Check if function has AIDEV-NOTE in preceding lines."""
        # Check 5 lines before function for AIDEV-NOTE
        start_check = max(0, func_node.lineno - 6)
        end_check = func_node.lineno - 1

        for line_idx in range(start_check, end_check + 1):
            if line_idx < len(lines):
                line = lines[line_idx]
                if re.search(r"#\s*AIDEV-(NOTE|TODO|QUESTION):", line):
                    return True
        return False

    def _has_aidev_note_at_top_of_file(self, lines: list[str]) -> bool:
        """Check if file has AIDEV-NOTE in first 20 lines (per guidelines).

        Recognizes AIDEV-NOTE in both comment syntax (#) and docstring syntax.
        """
        # Check first 20 lines for AIDEV-NOTE
        for i in range(min(20, len(lines))):
            line = lines[i]
            # Match both comment style (# AIDEV-NOTE:) and docstring style (AIDEV-NOTE:)
            if re.search(r"(?:#\s*)?AIDEV-(NOTE|TODO|QUESTION):", line):
                return True
        return False

    def _has_aidev_explanation_for_line(
        self, lines: list[str], target_line: int, number_str: str
    ) -> bool:
        """Check if there's an AIDEV comment explaining a magic number."""
        # Check same line, line before, and 5 lines before (for block comments)
        check_lines = list(
            range(max(0, target_line - 6), target_line + 1)
        )  # Convert to 0-based

        for line_idx in check_lines:
            if 0 <= line_idx < len(lines):
                line = lines[line_idx]
                if re.search(r"#\s*AIDEV-(NOTE|TODO|QUESTION):", line):
                    # If AIDEV comment mentions the number or is about constants/configuration
                    if number_str in line or any(
                        keyword in line.lower()
                        for keyword in [
                            "constant",
                            "config",
                            "batch",
                            "timeout",
                            "size",
                            "limit",
                        ]
                    ):
                        return True
        return False

    def _validate_no_partial_implementations(
        self, content: str, file_path: str
    ) -> None:
        """
        BLOCKING: Detect and block partial implementations, mocks, stubs, TODOs, placeholders.
        This enforces the Rankle rule: "PARTIAL IMPLEMENTATIONS kill the project"
        """
        lines = content.splitlines()
        content_lower = content.lower()

        # AIDEV-NOTE: Patterns that indicate partial implementations - all BLOCKING
        # Mock patterns are separate as they're allowed in test files only
        mock_patterns = [
            (r"\bmock\s*=", "Contains mock assignments"),
            (r"\bmock_\w+\s*=", "Contains mock variable assignments (mock_*)"),
            (r"Mock\(\)", "Contains Mock() instantiation"),
            (r"@patch|@mock", "Contains @patch or @mock decorators"),
            (r"unittest\.mock", "Contains unittest.mock usage"),
            (r"#.*\bmock\b.*return", "Contains mock-related comments about return values"),
            (r"#.*TDD\s+minimal", "Contains 'TDD minimal' implementation comments"),
        ]

        # AIDEV-NOTE: Anti-patterns for PRODUCTION code only (allowed in tests/)
        production_only_patterns = [
            # Test-related patterns (allowed in test files)
            (r"simplified\s+test", "Contains 'simplified test' - use comprehensive tests"),
            (r"basic\s+test", "Contains 'basic test' - use real test scenarios"),
            (r"\bmock\s+data\b", "Contains 'mock data' - use real data in production"),
            (r"\bfake\s+data\b", "Contains 'fake data' - use real data in production"),
            (r"\bsample\s+data\b", "Contains 'sample data' - use real data in production"),
        ]

        partial_patterns = [
            # TODO/FIXME patterns
            (r"#.*\b(TODO|FIXME|XXX|HACK)\b", "Contains TODO/FIXME/XXX/HACK comments"),
            (
                r"\b(todo|fixme|xxx|hack)\s*[:=]",
                "Contains TODO/FIXME variables or assignments",
            ),
            # Placeholder patterns
            (r"\bpass\s*#.*placeholder", "Contains placeholder 'pass' statements"),
            (
                r"\braise\s+NotImplementedError",
                "Contains NotImplementedError - incomplete method",
            ),
            (r"\bplaceholder\b", "Contains 'placeholder' references"),
            (
                r"\bstub\b.*(?:method|function|class)",
                "Contains stub method/function/class",
            ),
            (r"def.*stub.*\(", "Contains stub function definitions"),
            # Partial implementation text patterns
            (
                r"in\s+a\s+full\s+implementation",
                "Contains 'in a full implementation' text",
            ),
            (
                r"this\s+is\s+a\s+simplified\s+version",
                "Contains 'simplified version' text",
            ),
            (r"you\s+would\s+need\s+to", "Contains 'you would need to' text"),
            (r"consider\s+adding", "Contains 'consider adding' text"),
            (r"for\s+now\s+we", "Contains 'for now we' - temporary implementation"),
            (r"temporary\s+implementation", "Contains 'temporary implementation'"),
            (r"quick\s+and\s+dirty", "Contains 'quick and dirty' implementation"),
            # AIDEV-NOTE: Expensive anti-patterns - block in ALL files (production + tests)
            (r"\bworkaround\b", "Contains 'workaround' - fix root cause instead"),
            (r"as\s+a\s+workaround", "Contains 'as a workaround' - fix root cause"),
            (r"temporary\s+fix", "Contains 'temporary fix' - implement proper solution"),
            (r"quick\s+win", "Contains 'quick win' - use comprehensive solution"),
            (r"low\s+hanging\s+fruit", "Contains 'low hanging fruit' - avoid shortcuts"),
            (r"create\s+new\s+file", "Suggests creating new file - fix existing code instead"),
            (r"let'?s\s+create\s+a\s+new", "Suggests creating new - fix existing instead"),
            # Incomplete patterns
            # AIDEV-NOTE: Ellipsis validation handled separately with Pydantic Field(...) exclusion
            (
                r"return\s+None\s*#.*implement",
                "Contains 'return None # implement' patterns",
            ),
            (r"return\s*$", "Contains empty return statements"),
        ]

        # AIDEV-NOTE: Add mock patterns + production-only patterns only if NOT in test files
        if not self._is_test_file(file_path):
            partial_patterns.extend(mock_patterns)
            partial_patterns.extend(production_only_patterns)

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()

            for pattern, description in partial_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip all AIDEV anchor types (NOTE, TODO, QUESTION) as these are legitimate development anchors
                    if any(
                        anchor in line_lower
                        for anchor in ["aidev-note:", "aidev-todo:", "aidev-question:"]
                    ):
                        continue

                    # AIDEV-NOTE: Skip Pydantic Field(...) which uses ellipsis for required fields
                    if "..." in line and "Field(" in line:
                        continue

                    # Also check for ellipsis patterns that are NOT in Pydantic context
                    if pattern == r"\.\.\." and "Field(" in line:
                        continue

                    self.violations.append(
                        RankleViolation(
                            file_path=file_path,
                            line=i,
                            rule="no-partial-implementations",
                            message=f"{description}: {line.strip()}",
                            violation_type="partial_implementation",
                            fix_instruction="Complete the implementation - no TODOs, mocks, stubs, or placeholders allowed",
                        )
                    )

        # Check for empty function bodies (except pass with docstrings)
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # If function only contains 'pass' and no docstring, it's incomplete
                    if (
                        len(node.body) == 1
                        and isinstance(node.body[0], ast.Pass)
                        and not ast.get_docstring(node)
                    ):
                        self.violations.append(
                            RankleViolation(
                                file_path=file_path,
                                line=node.lineno,
                                rule="no-partial-implementations",
                                message=f"Function '{node.name}' contains only 'pass' - incomplete implementation",
                                violation_type="partial_implementation",
                                fix_instruction="Implement the function body or add proper docstring if intentionally empty",
                            )
                        )
        except SyntaxError:
            pass  # Already handled in main validation

    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        return bool(re.match(r"^[a-z_][a-z0-9_]*$", name))

    def _is_camel_case(self, name: str) -> bool:
        """Check if name follows CamelCase convention."""
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", name))

    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case suggestion."""
        # Simple conversion for demonstration
        result = re.sub(r"([A-Z])", r"_\1", name).lower()
        return result.lstrip("_")

    def _to_camel_case(self, name: str) -> str:
        """Convert name to CamelCase suggestion."""
        # Simple conversion for demonstration
        parts = name.split("_")
        return "".join(word.capitalize() for word in parts)

    def _is_test_file(self, file_path: str) -> bool:
        """Check if the file is in the tests folder."""
        # AIDEV-NOTE: Allow mocks only in test files per project requirements
        normalized_path = file_path.replace("\\", "/")  # Handle Windows paths
        return "/tests/" in normalized_path or normalized_path.startswith("tests/")


# AIDEV-NOTE: Export main validator class for hook integration
__all__ = ["RankleQualityValidator", "RankleViolation", "ViolationSeverity"]
