"""ETL loader entrypoint.

The loader is intentionally lightweight at this stage: it discovers the known
Sprint 1 source files, reads them with pandas, and emits a clean audit summary.
"""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)

RAW_FILES = (
	"companies.xlsx",
	"profitandloss.xlsx",
	"balancesheet.xlsx",
	"cashflow.xlsx",
	"analysis.xlsx",
	"documents.xlsx",
	"prosandcons.xlsx",
)

SUPPORTING_FILES = (
	"sectors.xlsx",
	"stock_prices.xlsx",
	"market_cap.xlsx",
	"financial_ratios.xlsx",
	"peer_groups.xlsx",
)


@dataclass(frozen=True)
class LoadRecord:
	source_file: str
	rows: int
	columns: int
	status: str
	message: str = ""


def discover_source_files(directory: Path, filenames: Iterable[str]) -> list[Path]:
	"""Return the source files that are present in ``directory``."""

	return [directory / filename for filename in filenames if (directory / filename).exists()]


def load_workbook(path: Path) -> pd.DataFrame:
	"""Load the first sheet from an Excel workbook as a DataFrame."""

	return pd.read_excel(path)


def load_directory(directory: Path, filenames: Iterable[str]) -> list[LoadRecord]:
	"""Load a set of expected Excel files and return a concise audit trail."""

	audit: list[LoadRecord] = []
	for file_path in discover_source_files(directory, filenames):
		try:
			frame = load_workbook(file_path)
			audit.append(
				LoadRecord(
					source_file=file_path.name,
					rows=len(frame.index),
					columns=len(frame.columns),
					status="loaded",
				)
			)
		except Exception as exc:  # pragma: no cover - surfaced through CLI use
			logger.exception("Failed to load %s", file_path)
			audit.append(
				LoadRecord(
					source_file=file_path.name,
					rows=0,
					columns=0,
					status="error",
					message=str(exc),
				)
			)
	return audit


def write_audit_csv(records: list[LoadRecord], output_path: Path) -> None:
	"""Persist the load audit to CSV in the format expected by the sprint brief."""

	output_path.parent.mkdir(parents=True, exist_ok=True)
	with output_path.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(
			handle,
			fieldnames=["source_file", "rows", "columns", "status", "message"],
		)
		writer.writeheader()
		writer.writerows(record.__dict__ for record in records)


def main() -> int:
	"""Command-line entrypoint for the Sprint 1 loader."""

	raw_dir = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
	supporting_dir = Path(os.getenv("SUPPORTING_DATA_DIR", "data/supporting"))
	output_dir = Path(os.getenv("OUTPUT_DIR", "output"))

	records = [
		*load_directory(raw_dir, RAW_FILES),
		*load_directory(supporting_dir, SUPPORTING_FILES),
	]

	write_audit_csv(records, output_dir / "load_audit.csv")
	logger.info("Wrote %d load audit rows", len(records))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

