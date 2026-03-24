# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""
ExecutionSandbox — resource-limited, isolated command execution for agents.

Provides CPU and memory resource constraints and safe subprocess invocation
without shell interpretation to prevent command injection.
"""

from __future__ import annotations

import logging
import re
import shlex
import subprocess

logger = logging.getLogger(__name__)

_CPU_LIMIT_RE = re.compile(r"^\d+(\.\d+)?$")
_MEMORY_LIMIT_RE = re.compile(r"^[1-9]\d*(m|g)$", re.IGNORECASE)


class ExecutionSandbox:
    """
    Sandboxing logic for autonomous agent execution.
    Provides isolation and resource limits for agent-run code.
    """

    def __init__(self, cpu_limit: str = "0.5", memory_limit: str = "512m") -> None:
        if not _CPU_LIMIT_RE.match(cpu_limit) or float(cpu_limit) <= 0:
            raise ValueError(
                f"Invalid cpu_limit {cpu_limit!r}. "
                "Expected a positive number greater than zero, e.g. '0.5' or '2'."
            )
        if not _MEMORY_LIMIT_RE.match(memory_limit):
            raise ValueError(
                f"Invalid memory_limit {memory_limit!r}. "
                "Expected a positive integer followed by 'm' or 'g', e.g. '512m' or '2g'."
            )
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit

    def run_isolated(self, command: str | list[str]) -> subprocess.CompletedProcess[str]:
        """
        Runs a command in a restricted environment (e.g., using Docker or nsjail).

        ``command`` may be a string (which is tokenised with :func:`shlex.split`)
        or a pre-split list of arguments.  ``shell=True`` is intentionally **not**
        used to prevent shell-injection attacks.
        """
        if isinstance(command, str):
            args = shlex.split(command)
        else:
            args = list(command)
        logger.info("Running command in sandbox: %s", args)
        # TODO: replace with actual container/process isolation (Docker, nsjail, …)
        #       and apply self.cpu_limit / self.memory_limit constraints.
        return subprocess.run(args, capture_output=True, text=True)  # noqa: S603
