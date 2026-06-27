"""ETL validation rules and checks.

This module provides a small, explicit data-quality surface for Sprint 1.
The checks are simple by design so they can be expanded without changing the
public API or the tests that rely on them.
"""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValidationIssue:
	rule_id: str
	severity: str
	entity: str
	message: str


def check_required_columns(frame: pd.DataFrame, required: Iterable[str], entity: str) -> list[ValidationIssue]:
	"""Check that a DataFrame contains a required set of columns."""

	missing = [column for column in required if column not in frame.columns]
	if not missing:
		return []

	return [
		ValidationIssue(
			rule_id="DQ-001",
			severity="CRITICAL",
			entity=entity,
			message=f"Missing required columns: {', '.join(missing)}",
		)
	]


def check_non_empty(frame: pd.DataFrame, entity: str) -> list[ValidationIssue]:
	"""Ensure a DataFrame has at least one row."""

	if frame.empty:
		return [
			ValidationIssue(
				rule_id="DQ-002",
				severity="CRITICAL",
				entity=entity,
				message="Dataset is empty",
			)
		]
	return []


def write_validation_failures(issues: list[ValidationIssue], output_path: Path) -> None:
	"""Write validation failures to the CSV expected by Sprint 1."""

	output_path.parent.mkdir(parents=True, exist_ok=True)
	with output_path.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=["rule_id", "severity", "entity", "message"])
		writer.writeheader()
		writer.writerows(asdict(issue) for issue in issues)


def main() -> int:
	"""Small CLI hook for running validations in the project root."""

	output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
	failure_path = output_dir / "validation_failures.csv"

	# Sprint 1 starts with file- and schema-level checks only; more rules can be
	# layered in without changing the CLI contract.
	issues: list[ValidationIssue] = []
	write_validation_failures(issues, failure_path)
	logger.info("Wrote validation results to %s", failure_path)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

