"""ETL normalisation utilities.

This module keeps the Sprint 1 data foundation rules in one place so raw
Screener-style labels can be normalised before they touch the database layer.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

MONTH_MAP: dict[str, str] = {
	"Jan": "01",
	"Feb": "02",
	"Mar": "03",
	"Apr": "04",
	"May": "05",
	"Jun": "06",
	"Jul": "07",
	"Aug": "08",
	"Sep": "09",
	"Oct": "10",
	"Nov": "11",
	"Dec": "12",
	"January": "01",
	"February": "02",
	"March": "03",
	"April": "04",
	"June": "06",
	"July": "07",
	"August": "08",
	"September": "09",
	"October": "10",
	"November": "11",
	"December": "12",
}

YEAR_TABLES = {"profitandloss", "balancesheet", "cashflow", "financial_ratios"}


def _is_missing(value: Any) -> bool:
	return value is None or (isinstance(value, float) and pd.isna(value))


def normalize_year(raw: Any) -> str:
	"""Normalize known year labels to ``YYYY-MM``.

	Unknown formats return ``PARSE_ERROR`` so the validation layer can record
	them explicitly instead of failing silently.
	"""

	if _is_missing(raw):
		return "PARSE_ERROR"

	raw_str = str(raw).strip()

	if re.fullmatch(r"\d{4}-\d{2}", raw_str):
		return raw_str

	fy_match = re.fullmatch(r"FY(\d{2,4})", raw_str, flags=re.IGNORECASE)
	if fy_match:
		year_part = fy_match.group(1)
		year = int(f"20{year_part}") if len(year_part) == 2 else int(year_part)
		return f"{year}-03"

	short_match = re.fullmatch(r"([A-Za-z]{3,9})[-\s](\d{2})", raw_str)
	if short_match:
		month_raw = short_match.group(1).title()
		year = 2000 + int(short_match.group(2))
		month = MONTH_MAP.get(month_raw[:3], MONTH_MAP.get(month_raw, "03"))
		return f"{year}-{month}"

	long_match = re.fullmatch(r"([A-Za-z]+)[-\s](\d{4})", raw_str)
	if long_match:
		month_raw = long_match.group(1).title()
		month = MONTH_MAP.get(month_raw[:3], MONTH_MAP.get(month_raw, "03"))
		return f"{long_match.group(2)}-{month}"

	if re.fullmatch(r"\d{4}", raw_str):
		return f"{raw_str}-03"

	logger.warning("normalize_year: unrecognised format '%s'", raw_str)
	return "PARSE_ERROR"


def normalize_ticker(raw: Any) -> str:
	"""Normalize a company identifier to the cleaned ticker form."""

	if _is_missing(raw):
		return "MISSING"

	ticker = str(raw).strip().upper()
	if not ticker:
		return "MISSING"

	ticker = re.sub(r"\.(NS|BSE|NSE)$", "", ticker)
	ticker = re.sub(r"\s+", "", ticker)

	if len(ticker) < 2 or len(ticker) > 12:
		logger.warning("normalize_ticker: length out of range for '%s'", ticker)
		return "INVALID"

	return ticker


def normalize_company_id(raw: Any) -> str:
	"""Backward-compatible alias for the company identifier normaliser."""

	return normalize_ticker(raw)


def _coerce_nullable_int(series: pd.Series) -> pd.Series:
	return pd.to_numeric(series, errors="coerce").astype("Int64")


def _coerce_benchmark_flag(series: pd.Series) -> pd.Series:
	def convert(value: Any) -> int | None:
		if value is None or pd.isna(value):
			return None
		if isinstance(value, str):
			value = value.strip().lower()
			if value in {"1", "true", "yes", "y"}:
				return 1
			if value in {"0", "false", "no", "n"}:
				return 0
		return 1 if bool(value) else 0

	return series.map(convert).astype("Int64")


def apply_normalisation(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
	"""Apply the table-specific normalisation rules used by Sprint 1."""

	frame = df.copy()

	if "company_id" in frame.columns:
		frame["company_id"] = frame["company_id"].apply(normalize_ticker)

	if table_name == "companies" and "id" in frame.columns:
		frame["id"] = frame["id"].apply(normalize_ticker)

	if table_name in YEAR_TABLES and "year" in frame.columns:
		frame["year"] = frame["year"].apply(normalize_year)

	if table_name == "documents" and "Year" in frame.columns:
		frame["Year"] = _coerce_nullable_int(frame["Year"])

	if table_name == "market_cap" and "year" in frame.columns:
		frame["year"] = _coerce_nullable_int(frame["year"])

	if table_name == "peer_groups" and "is_benchmark" in frame.columns:
		frame["is_benchmark"] = _coerce_benchmark_flag(frame["is_benchmark"])

	return frame

