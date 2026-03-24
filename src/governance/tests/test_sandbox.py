# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Tests for ExecutionSandbox (src/governance/sandboxing/sandbox.py)."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from governance.sandboxing.sandbox import ExecutionSandbox


# ---------------------------------------------------------------------------
# Initialisation / validation
# ---------------------------------------------------------------------------


class TestExecutionSandboxInit:
    """ExecutionSandbox.__init__ validates resource-limit parameters."""

    def test_default_params(self) -> None:
        sb = ExecutionSandbox()
        assert sb.cpu_limit == "0.5"
        assert sb.memory_limit == "512m"

    def test_custom_valid_params(self) -> None:
        sb = ExecutionSandbox(cpu_limit="2", memory_limit="1g")
        assert sb.cpu_limit == "2"
        assert sb.memory_limit == "1g"

    def test_decimal_cpu_limit(self) -> None:
        sb = ExecutionSandbox(cpu_limit="1.5")
        assert sb.cpu_limit == "1.5"

    @pytest.mark.parametrize("bad_cpu", ["abc", "-1", "0.5.5", "", "1 cpu", "; rm -rf /", "0", "0.0"])
    def test_invalid_cpu_limit_raises(self, bad_cpu: str) -> None:
        with pytest.raises(ValueError, match="cpu_limit"):
            ExecutionSandbox(cpu_limit=bad_cpu)

    @pytest.mark.parametrize("bad_mem", ["512", "abc", "-1m", "1tb", "", "512m; evil", "1G1", "0m", "0g"])
    def test_invalid_memory_limit_raises(self, bad_mem: str) -> None:
        with pytest.raises(ValueError, match="memory_limit"):
            ExecutionSandbox(memory_limit=bad_mem)

    def test_memory_limit_case_insensitive(self) -> None:
        sb_upper = ExecutionSandbox(memory_limit="512M")
        assert sb_upper.memory_limit == "512M"
        sb_upper_g = ExecutionSandbox(memory_limit="2G")
        assert sb_upper_g.memory_limit == "2G"


# ---------------------------------------------------------------------------
# run_isolated — no shell=True (command injection prevention)
# ---------------------------------------------------------------------------


class TestRunIsolatedSecurity:
    """run_isolated must never invoke a shell interpreter."""

    def test_shell_not_used(self) -> None:
        """subprocess.run must be called without shell=True."""
        sb = ExecutionSandbox()
        with patch("governance.sandboxing.sandbox.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(spec=subprocess.CompletedProcess)
            sb.run_isolated("echo hello")
            _, kwargs = mock_run.call_args
            assert kwargs.get("shell", False) is False, "shell=True must not be used"

    def test_string_command_is_split(self) -> None:
        """A string command is tokenised; the shell is not invoked."""
        sb = ExecutionSandbox()
        with patch("governance.sandboxing.sandbox.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(spec=subprocess.CompletedProcess)
            sb.run_isolated("echo hello world")
            args, _ = mock_run.call_args
            # First positional arg should be a list, not a raw string
            assert isinstance(args[0], list)
            assert args[0] == ["echo", "hello", "world"]

    def test_list_command_passed_through(self) -> None:
        """A pre-split list is forwarded as-is."""
        sb = ExecutionSandbox()
        with patch("governance.sandboxing.sandbox.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(spec=subprocess.CompletedProcess)
            sb.run_isolated(["echo", "hello"])
            args, _ = mock_run.call_args
            assert args[0] == ["echo", "hello"]

    def test_shell_metacharacters_not_interpreted(self) -> None:
        """Shell metacharacters in commands are treated as literals, not executed."""
        sb = ExecutionSandbox()
        with patch("governance.sandboxing.sandbox.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(spec=subprocess.CompletedProcess)
            # This would be dangerous with shell=True; safe as a token list
            sb.run_isolated("echo safe && echo injected")
            args, kwargs = mock_run.call_args
            assert kwargs.get("shell", False) is False
            # shlex splits on whitespace, treating && as a literal token
            assert "&&" in args[0]


# ---------------------------------------------------------------------------
# run_isolated — basic behaviour
# ---------------------------------------------------------------------------


class TestRunIsolatedBehaviour:
    """run_isolated returns subprocess results correctly."""

    def test_returns_completed_process(self) -> None:
        sb = ExecutionSandbox()
        result = sb.run_isolated(["echo", "hello"])
        assert isinstance(result, subprocess.CompletedProcess)
        assert "hello" in result.stdout

    def test_capture_output(self) -> None:
        sb = ExecutionSandbox()
        result = sb.run_isolated(["echo", "captured"])
        assert result.stdout.strip() == "captured"
        assert result.stderr == ""
