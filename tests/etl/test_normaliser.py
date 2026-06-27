"""Tests for ETL normalisation."""

from src.etl.normaliser import normalize_company_id, normalize_ticker, normalize_year


def test_normalize_year_handles_short_month_label() -> None:
	assert normalize_year("Mar-23") == "2023-03"


def test_normalize_year_handles_fy_label() -> None:
	assert normalize_year("FY24") == "2024-03"


def test_normalize_ticker_strips_suffixes_and_caps() -> None:
	assert normalize_ticker(" infy.ns ") == "INFY"


def test_normalize_company_id_alias_matches_ticker() -> None:
	assert normalize_company_id("tcs.bse") == "TCS"

