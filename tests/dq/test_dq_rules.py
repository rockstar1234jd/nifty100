"""Tests for data quality rules."""

import pandas as pd

from src.etl.validator import check_non_empty, check_required_columns


def test_check_required_columns_flags_missing_fields() -> None:
	frame = pd.DataFrame({"company": ["TCS"]})

	issues = check_required_columns(frame, ["company", "year"], "companies")

	assert len(issues) == 1
	assert issues[0].severity == "CRITICAL"


def test_check_non_empty_reports_empty_frames() -> None:
	frame = pd.DataFrame(columns=["company"])

	issues = check_non_empty(frame, "companies")

	assert len(issues) == 1
	assert issues[0].rule_id == "DQ-002"

