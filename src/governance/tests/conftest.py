# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Pytest configuration: add src/ to sys.path so governance package is importable."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
