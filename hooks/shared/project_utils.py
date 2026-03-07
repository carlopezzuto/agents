#!/usr/bin/env python3
"""
Project utilities for detecting project root and virtual environments.
"""

import os
import sys
from pathlib import Path


def get_project_root_from_file(file_path: str) -> Path | None:
    """
    Detect project root from a file path by looking for project indicators.

    Strategy:
    1. Walk up directory tree from the file
    2. Look for these indicators (in priority order):
       - .venv or venv directory (virtual environment)
       - pyproject.toml or setup.py (Python project config)
       - .git directory (git repository root)
       - requirements.txt or Pipfile (dependency files)
       - CLAUDE.md (project documentation)

    Args:
        file_path: Path to a file in the project

    Returns:
        Path to project root, or None if not found
    """
    try:
        path = Path(file_path)

        # Start from the file's directory
        current_dir = path.parent if path.is_file() else path

        # Check up to 10 levels up (reasonable limit)
        for parent in [current_dir] + list(current_dir.parents)[:10]:
            # Check for virtual environment directories
            venv_indicators = [".venv", "venv", "env", ".env"]
            for venv_name in venv_indicators:
                venv_path = parent / venv_name
                if venv_path.is_dir() and (venv_path / "bin").exists():
                    return parent
                if venv_path.is_dir() and (venv_path / "Scripts").exists():  # Windows
                    return parent

            # Check for Python project files
            project_files = ["pyproject.toml", "setup.py", "setup.cfg"]
            for project_file in project_files:
                if (parent / project_file).exists():
                    return parent

            # Check for .git directory (repository root)
            if (parent / ".git").is_dir():
                return parent

            # Check for dependency files
            if (parent / "requirements.txt").exists() or (parent / "Pipfile").exists():
                return parent

            # Check for CLAUDE.md (project-specific)
            if (parent / "CLAUDE.md").exists():
                return parent

            # For Rankle specifically, check for distinctive directories
            if (parent / "src" / "ontology").exists() and (
                parent / "src" / "ml_pipeline"
            ).exists():
                return parent

        return None

    except Exception:
        return None


def find_venv_python(project_root: Path) -> tuple[Path | None, dict | None]:
    """
    Find the virtual environment Python and set up environment variables.

    Args:
        project_root: Root directory of the project

    Returns:
        Tuple of (venv_python_path, env_dict)
    """
    # Check for various virtual environment names
    venv_names = [".venv", "venv", "env", ".env"]

    for venv_name in venv_names:
        venv_path = project_root / venv_name

        # Check for Unix-like systems
        venv_python = venv_path / "bin" / "python"
        if venv_python.exists():
            env = os.environ.copy()
            venv_bin = venv_path / "bin"
            env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
            env["VIRTUAL_ENV"] = str(venv_path)
            return venv_python, env

        # Check for Windows
        venv_python = venv_path / "Scripts" / "python.exe"
        if venv_python.exists():
            env = os.environ.copy()
            venv_scripts = venv_path / "Scripts"
            env["PATH"] = f"{venv_scripts};{env.get('PATH', '')}"
            env["VIRTUAL_ENV"] = str(venv_path)
            return venv_python, env

    # Check if we're already in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        # We're in a virtual environment
        env = os.environ.copy()
        return Path(sys.executable), env

    # Check VIRTUAL_ENV environment variable
    if "VIRTUAL_ENV" in os.environ:
        venv_path = Path(os.environ["VIRTUAL_ENV"])
        venv_python = venv_path / "bin" / "python"
        if not venv_python.exists():
            venv_python = venv_path / "Scripts" / "python.exe"
        if venv_python.exists():
            return venv_python, os.environ.copy()

    return None, None


def get_venv_tool_path(project_root: Path, tool_name: str) -> str | None:
    """
    Get the path to a tool in the virtual environment.

    Args:
        project_root: Root directory of the project
        tool_name: Name of the tool (e.g., 'black', 'ruff')

    Returns:
        Full path to the tool, or just the tool name if not in venv
    """
    venv_names = [".venv", "venv", "env", ".env"]

    for venv_name in venv_names:
        venv_path = project_root / venv_name

        # Unix-like systems
        tool_path = venv_path / "bin" / tool_name
        if tool_path.exists():
            return str(tool_path)

        # Windows
        tool_path = venv_path / "Scripts" / f"{tool_name}.exe"
        if tool_path.exists():
            return str(tool_path)

        # Windows without .exe
        tool_path = venv_path / "Scripts" / tool_name
        if tool_path.exists():
            return str(tool_path)

    # Fallback to system tool
    return tool_name
