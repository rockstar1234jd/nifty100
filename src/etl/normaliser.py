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
		return ""

	ticker = str(raw).strip().upper()
	ticker = re.sub(r"\s+", " ", ticker)
	ticker = ticker.replace(".NS", "").replace(".BSE", "")
	return ticker


def normalize_company_id(raw: Any) -> str:
	"""Backward-compatible alias for the company identifier normaliser."""

	return normalize_ticker(raw)

