"""Tests for ETL loading."""

from pathlib import Path

from src.etl.loader import discover_source_files


def test_discover_source_files_returns_only_existing_files(tmp_path: Path) -> None:
	existing = tmp_path / "companies.xlsx"
	existing.write_text("stub", encoding="utf-8")

	files = discover_source_files(tmp_path, ["companies.xlsx", "missing.xlsx"])

	assert files == [existing]

