#!/usr/bin/env python3
"""
Quality Toolchain - Formatting and Linting Tools Integration

This module runs quality tools (ruff, black, pyright) and categorizes issues:
- Auto-fixable: Issues tools can fix automatically (black, ruff --fix)
- Unsafe fixes: Fixes that might change behavior (ruff --unsafe-fixes)
- Manual required: Issues that must be fixed by hand (type errors, complex linting)

Note: Import sorting is handled by ruff's isort functionality (no separate isort tool).

ALL issues result in BLOCKING - no exceptions.
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ToolIssue:
    """Represents an issue found by a quality tool."""

    tool: str
    file_path: str
    line: int
    column: int = 0
    rule: str = ""
    message: str = ""
    severity: str = "error"
    fix_available: bool = False
    is_unsafe_fix: bool = False

    def __str__(self):
        return f"{self.tool}: {self.file_path}:{self.line}:{self.column} {self.rule} - {self.message}"


@dataclass
class ToolchainResult:
    """Results from running all quality tools."""

    file_path: str = ""

    # Tool-specific results
    ruff_issues: list[ToolIssue] = field(default_factory=list)
    black_issues: list[ToolIssue] = field(default_factory=list)
    # isort_issues: Removed - using ruff's isort functionality instead
    pyright_issues: list[ToolIssue] = field(default_factory=list)

    # Categorized fixes
    auto_fixable_issues: list[ToolIssue] = field(default_factory=list)
    unsafe_fix_issues: list[ToolIssue] = field(default_factory=list)
    manual_fix_issues: list[ToolIssue] = field(default_factory=list)

    # Overall status
    has_any_issues: bool = False
    needs_formatting: bool = False
    needs_import_sorting: bool = False
    has_type_errors: bool = False

    # Commands to run
    auto_fix_commands: list[str] = field(default_factory=list)
    unsafe_fix_commands: list[str] = field(default_factory=list)

    def get_total_issues(self) -> int:
        """Get total number of issues across all tools."""
        return (
            len(self.ruff_issues)
            + len(self.black_issues)
            + len(self.pyright_issues)
        )

    def get_blocking_summary(self) -> str:
        """Get summary of all blocking issues."""
        total = self.get_total_issues()
        if total == 0:
            return "✅ No quality issues found"

        summary = f"❌ {total} quality issues found (ALL BLOCKING):\n"

        if self.auto_fixable_issues:
            summary += f"  🔧 {len(self.auto_fixable_issues)} auto-fixable\n"
        if self.unsafe_fix_issues:
            summary += f"  ⚠️ {len(self.unsafe_fix_issues)} unsafe fixes available\n"
        if self.manual_fix_issues:
            summary += f"  ✋ {len(self.manual_fix_issues)} require manual fixes\n"

        return summary


class QualityToolchain:
    """
    Runs all quality tools and categorizes issues for proper handling.
    ALL issues are treated as BLOCKING.
    """

    def __init__(self, project_root: str = "", file_path: str = ""):
        # Import project utilities
        from project_utils import get_project_root_from_file, get_venv_tool_path

        # Determine project root intelligently
        if project_root:
            self.project_root = Path(project_root)
        elif file_path:
            # Try to detect project root from file path
            detected_root = get_project_root_from_file(file_path)
            self.project_root = detected_root if detected_root else Path.cwd()
        else:
            self.project_root = Path.cwd()

        # Tool configurations
        self.ruff_config = {"line_length": 88, "target_version": "py310"}

        self.black_config = {
            "line_length": 88,
            "target_version": ["py310", "py311", "py312"],
        }

        # Find pyproject.toml by walking up from project root
        root = self.project_root
        for candidate in [root] + list(root.parents):
            if (candidate / "pyproject.toml").exists():
                root = candidate
                break

        # Set final project root and config file paths (FIXED: moved outside loop)
        self.project_root = root
        self.pyproject = self.project_root / "pyproject.toml"
        self.pyrightconfig = self.project_root / "pyrightconfig.json"

        # Set up environment and tool paths
        self.env = os.environ.copy()

        # Try to find tools in virtual environment
        self.ruff_bin = get_venv_tool_path(self.project_root, "ruff")
        self.black_bin = get_venv_tool_path(self.project_root, "black")
        # self.isort_bin = get_venv_tool_path(self.project_root, "isort")  # Removed - using ruff
        self.pyright_bin = get_venv_tool_path(self.project_root, "pyright")

        # Update PATH to include venv bin directory if it exists
        venv_names = [".venv", "venv", "env", ".env"]
        for venv_name in venv_names:
            venv_bin = (
                self.project_root
                / venv_name
                / ("Scripts" if os.name == "nt" else "bin")
            )
            if venv_bin.exists():
                self.env["PATH"] = f"{venv_bin!s}{os.pathsep}{self.env.get('PATH','')}"
                break

    def run_all(self, file_path: str, original_path: str | None = None) -> ToolchainResult:
        """
        Run all quality tools on the file and categorize issues.

        Args:
            file_path: Actual file path to check (may be temp file)
            original_path: Original file path for per-file-ignore matching (optional)

        Returns comprehensive result with categorized fixes.
        """
        # Use original_path for rule matching if provided, otherwise use file_path
        path_for_rules = original_path if original_path else file_path
        result = ToolchainResult(file_path=path_for_rules)

        if not Path(file_path).exists():
            # Create a manual issue for missing file
            result.manual_fix_issues.append(
                ToolIssue(
                    tool="filesystem",
                    file_path=path_for_rules,
                    line=1,
                    message=f"File does not exist: {file_path}",
                    rule="file-not-found",
                )
            )
            result.has_any_issues = True
            return result

        if not file_path.endswith(".py"):
            # Only process Python files
            return result

        # Run each tool (pass both paths for stdin-filename support)
        self._run_ruff(file_path, result, original_path=path_for_rules)
        self._run_black(file_path, result)
        # self._run_isort(file_path, result)  # Removed - using ruff's isort functionality
        self._run_pyright(file_path, result, original_path=path_for_rules)

        # Categorize all issues
        self._categorize_issues(result)

        # Generate fix commands
        self._generate_fix_commands(path_for_rules, result)

        # Set overall status
        result.has_any_issues = result.get_total_issues() > 0

        return result

    def _run_ruff(self, file_path: str, result: ToolchainResult, original_path: str | None = None) -> None:
        """Run ruff linter and categorize fixes.

        Args:
            file_path: Actual file to check (may be temp file)
            result: ToolchainResult to populate
            original_path: Original file path for per-file-ignore matching
        """
        try:
            # 1. Check all issues
            # AIDEV-NOTE: Use stdin with --stdin-filename when original_path differs
            # This allows ruff to match per-file-ignores patterns like "scripts/**/*.py"
            # while analyzing temp file content
            if original_path and original_path != file_path:
                cmd = [self.ruff_bin, "check", "--stdin-filename", original_path, "--output-format=json"]
                if self.pyproject.exists():
                    cmd += ["--config", str(self.pyproject)]

                # Read file content to pass via stdin
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except Exception:
                    file_content = ""

                ruff_check = subprocess.run(
                    cmd,
                    input=file_content,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.project_root),
                    env=self.env,
                )
            else:
                cmd = [self.ruff_bin, "check", file_path, "--output-format=json"]
                if self.pyproject.exists():
                    cmd += ["--config", str(self.pyproject)]

                ruff_check = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.project_root),
                    env=self.env,
                )

            if ruff_check.stdout.strip():
                try:
                    ruff_data = json.loads(ruff_check.stdout)
                    for issue_data in ruff_data:
                        issue = ToolIssue(
                            tool="ruff",
                            file_path=issue_data.get("filename", file_path),
                            line=issue_data.get("location", {}).get("row", 1),
                            column=issue_data.get("location", {}).get("column", 0),
                            rule=issue_data.get("code", ""),
                            message=issue_data.get("message", ""),
                            severity="error",
                            fix_available=issue_data.get("fix", {}) is not None,
                        )
                        # AIDEV-NOTE: Validate that violation location exists in file
                        if self._is_valid_violation_location(file_path, issue):
                            result.ruff_issues.append(issue)
                except json.JSONDecodeError:
                    # Fallback to parsing text output if JSON fails
                    self._parse_ruff_text_output(ruff_check.stdout, file_path, result)

            # 2. Check which are auto-fixable (safe fixes only)
            # Note: --fix with stdin is not well supported, so we skip auto-fix checking for temp files
            # The fix_available flag is already set from the first check based on ruff's fix suggestions
            if original_path and original_path != file_path:
                # For temp files, trust the fix_available flag from the initial check
                pass
            else:
                cmd = [self.ruff_bin, "check", file_path, "--fix", "--dry-run", "--diff"]
                if self.pyproject.exists():
                    cmd += ["--config", str(self.pyproject)]

                ruff_fix_check = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.project_root),
                    env=self.env,
                )

                # If there's diff output, there are auto-fixable issues
                if ruff_fix_check.stdout.strip():
                    # Mark corresponding issues as auto-fixable
                    for issue in result.ruff_issues:
                        if issue.fix_available:
                            issue.fix_available = True

            # 3. Check unsafe fixes
            # Note: --unsafe-fixes with stdin is not well supported, so we skip for temp files
            if original_path and original_path != file_path:
                # For temp files, skip unsafe fix detection
                pass
            else:
                cmd = [
                    self.ruff_bin,
                    "check",
                    file_path,
                    "--unsafe-fixes",
                    "--dry-run",
                    "--diff",
                ]
                if self.pyproject.exists():
                    cmd += ["--config", str(self.pyproject)]

                ruff_unsafe_check = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.project_root),
                    env=self.env,
                )

                # Mark issues with unsafe fixes
                if ruff_unsafe_check.stdout.strip() and len(ruff_unsafe_check.stdout) > len(
                    ruff_fix_check.stdout
                ):
                    for issue in result.ruff_issues:
                        # If unsafe diff is longer than safe diff, there are unsafe fixes
                        if not issue.fix_available:  # Not already marked as auto-fixable
                            issue.is_unsafe_fix = True

        except subprocess.TimeoutExpired:
            result.ruff_issues.append(
                ToolIssue(
                    tool="ruff",
                    file_path=file_path,
                    line=1,
                    message="Ruff execution timed out",
                    rule="timeout",
                )
            )
        except FileNotFoundError:
            result.ruff_issues.append(
                ToolIssue(
                    tool="ruff",
                    file_path=file_path,
                    line=1,
                    message="Ruff not found - install with: pip install ruff",
                    rule="tool-missing",
                )
            )

    def _run_black(self, file_path: str, result: ToolchainResult) -> None:
        """Run black formatter check."""
        try:
            cmd = [
                self.black_bin,
                "--check",
                "--diff",
                "--line-length",
                "88",
                file_path,
            ]
            if self.pyproject.exists():
                cmd += ["--config", str(self.pyproject)]
            
            black_check = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root),
                env=self.env,
            )

            if black_check.returncode != 0:
                result.needs_formatting = True
                # Parse diff to find specific issues
                if black_check.stdout.strip():
                    lines_changed = self._count_diff_lines(black_check.stdout)
                    result.black_issues.append(
                        ToolIssue(
                            tool="black",
                            file_path=file_path,
                            line=1,  # Generic line since it affects whole file
                            message=f"File needs formatting ({lines_changed} lines would change)",
                            rule="format-required",
                            fix_available=True,  # Black can auto-fix
                        )
                    )
                else:
                    result.black_issues.append(
                        ToolIssue(
                            tool="black",
                            file_path=file_path,
                            line=1,
                            message="File needs formatting",
                            rule="format-required",
                            fix_available=True,
                        )
                    )

        except subprocess.TimeoutExpired:
            result.black_issues.append(
                ToolIssue(
                    tool="black",
                    file_path=file_path,
                    line=1,
                    message="Black execution timed out",
                    rule="timeout",
                )
            )
        except FileNotFoundError:
            result.black_issues.append(
                ToolIssue(
                    tool="black",
                    file_path=file_path,
                    line=1,
                    message="Black not found - install with: pip install black",
                    rule="tool-missing",
                )
            )

    # _run_isort method removed - import sorting now handled by ruff's isort functionality

    def _run_pyright(self, file_path: str, result: ToolchainResult, original_path: str | None = None) -> None:
        """
        Run pyright type checker.

        Args:
            file_path: Actual file path to check (may be temp file)
            result: ToolchainResult to append issues to
            original_path: Original file path for context (optional)
        """
        try:
            # AIDEV-NOTE: Detect if we're checking a temp file for relative import handling
            is_temp_file = file_path.startswith(("/tmp/", "/var/tmp/")) and original_path and original_path != file_path

            cmd = [self.pyright_bin, "--outputjson", file_path]

            # Enhance environment for pyright to resolve imports properly
            pyright_env = self.env.copy()

            # Add project src to PYTHONPATH so imports can be resolved
            # AIDEV-NOTE: Support both src/ and python-service/ project structures
            python_paths = []

            # Check for src/ directory (TypeScript projects)
            src_path = self.project_root / "src"
            if src_path.exists():
                python_paths.append(str(src_path))

            # Check for python-service/ directory (Python backend projects)
            python_service_path = self.project_root / "python-service"
            if python_service_path.exists():
                python_paths.append(str(python_service_path))

            # Add paths to PYTHONPATH if any were found
            if python_paths:
                paths_str = os.pathsep.join(python_paths)
                if "PYTHONPATH" in pyright_env:
                    pyright_env["PYTHONPATH"] = f"{paths_str}{os.pathsep}{pyright_env['PYTHONPATH']}"
                else:
                    pyright_env["PYTHONPATH"] = paths_str
            
            pyright_check = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_root),
                env=pyright_env,
            )

            if pyright_check.stdout.strip():
                try:
                    pyright_data = json.loads(pyright_check.stdout)

                    # Check for diagnostics
                    if "generalDiagnostics" in pyright_data:
                        for diagnostic in pyright_data["generalDiagnostics"]:
                            if diagnostic.get("file") == file_path:
                                # AIDEV-NOTE: Skip reportMissingImports for relative imports in temp files
                                # Relative imports (starting with '.') can't be resolved from /tmp/
                                # without the proper package directory structure
                                rule = diagnostic.get("rule", "type-error")
                                message = diagnostic.get("message", "")

                                if is_temp_file and rule == "reportMissingImports":
                                    # Check if it's a relative import (message contains '".' or "'.")
                                    if ('".') in message or ("'.") in message:
                                        continue  # Skip this diagnostic for temp file validation

                                severity = diagnostic.get("severity", "error")
                                if severity in [
                                    "error",
                                    "warning",
                                ]:  # Include warnings as blocking
                                    result.has_type_errors = True
                                    result.pyright_issues.append(
                                        ToolIssue(
                                            tool="pyright",
                                            file_path=original_path if original_path else file_path,
                                            line=diagnostic.get("range", {})
                                            .get("start", {})
                                            .get("line", 1)
                                            + 1,
                                            column=diagnostic.get("range", {})
                                            .get("start", {})
                                            .get("character", 0),
                                            rule=rule,
                                            message=message,
                                            severity=severity,
                                            fix_available=False,  # Type errors usually need manual fixes
                                        )
                                    )

                except json.JSONDecodeError:
                    # Fallback for non-JSON output
                    if pyright_check.stderr.strip():
                        result.pyright_issues.append(
                            ToolIssue(
                                tool="pyright",
                                file_path=file_path,
                                line=1,
                                message=f"Type checking error: {pyright_check.stderr.strip()}",
                                rule="type-check-failed",
                            )
                        )

        except subprocess.TimeoutExpired:
            result.pyright_issues.append(
                ToolIssue(
                    tool="pyright",
                    file_path=file_path,
                    line=1,
                    message="Pyright execution timed out",
                    rule="timeout",
                )
            )
        except FileNotFoundError:
            result.pyright_issues.append(
                ToolIssue(
                    tool="pyright",
                    file_path=file_path,
                    line=1,
                    message="Pyright not found - install with: npm install -g pyright",
                    rule="tool-missing",
                )
            )

    def _categorize_issues(self, result: ToolchainResult) -> None:
        """Categorize all issues into auto-fixable, unsafe fixes, and manual."""
        all_issues = (
            result.ruff_issues
            + result.black_issues
            + result.pyright_issues
        )

        for issue in all_issues:
            if issue.fix_available and not issue.is_unsafe_fix:
                result.auto_fixable_issues.append(issue)
            elif issue.is_unsafe_fix:
                result.unsafe_fix_issues.append(issue)
            else:
                result.manual_fix_issues.append(issue)

    def _generate_fix_commands(self, file_path: str, result: ToolchainResult) -> None:
        """Generate commands to fix issues."""
        # Auto-fix commands
        if result.needs_formatting:
            result.auto_fix_commands.append(f"black --line-length 88 {file_path}")

        # Import sorting now handled by ruff (no separate isort command needed)

        if any(issue.fix_available for issue in result.ruff_issues):
            result.auto_fix_commands.append(f"ruff check --fix {file_path}")

        # Unsafe fix commands
        if any(issue.is_unsafe_fix for issue in result.ruff_issues):
            result.unsafe_fix_commands.append(
                f"ruff check --unsafe-fixes --diff {file_path}"
            )
            result.unsafe_fix_commands.append(
                f"ruff check --unsafe-fixes --fix {file_path}"
            )

    def _parse_ruff_text_output(
        self, output: str, file_path: str, result: ToolchainResult
    ) -> None:
        """Parse ruff text output as fallback."""
        for line in output.splitlines():
            if file_path in line and ":" in line:
                # Basic parsing: file:line:col: rule - message
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    try:
                        line_num = int(parts[1])
                        col_num = int(parts[2])
                        message_part = parts[3].strip()

                        rule = ""
                        message = message_part
                        if " " in message_part:
                            potential_rule = message_part.split()[0]
                            if len(potential_rule) < 10:  # Likely a rule code
                                rule = potential_rule
                                message = message_part[len(rule) :].strip()

                        result.ruff_issues.append(
                            ToolIssue(
                                tool="ruff",
                                file_path=file_path,
                                line=line_num,
                                column=col_num,
                                rule=rule,
                                message=message,
                            )
                        )
                    except ValueError:
                        # Skip lines that don't match expected format
                        continue

    def _count_diff_lines(self, diff_output: str) -> int:
        """Count number of lines that would change in diff."""
        lines = diff_output.splitlines()
        change_count = 0
        for line in lines:
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                change_count += 1
        return change_count

    def _is_valid_violation_location(self, file_path: str, issue: ToolIssue) -> bool:
        """
        Validate that a violation's line and column numbers are within file bounds.

        This prevents reporting impossible violations like "character 279 on line 1"
        when line 1 is only 81 characters long.

        Args:
            file_path: Path to file being checked
            issue: ToolIssue to validate

        Returns:
            True if violation location is valid, False otherwise
        """
        try:
            # Read file to check bounds
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Check line number is valid
            if issue.line < 1 or issue.line > len(lines):
                return False

            # Check column number is valid (if specified)
            if issue.column > 0:
                line_content = lines[issue.line - 1]  # Convert to 0-indexed
                # Remove newline for length check
                line_length = len(line_content.rstrip('\n\r'))
                if issue.column > line_length:
                    return False

            return True

        except Exception:
            # If we can't read the file, allow the violation through
            # (it might be a temp file that's already been cleaned up)
            return True


# AIDEV-NOTE: Export main toolchain class and result types for hook integration
__all__ = ["QualityToolchain", "ToolIssue", "ToolchainResult"]
