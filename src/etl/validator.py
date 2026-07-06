"""ETL validation rules and checks.

This module keeps the lightweight helper functions used by the existing tests
and adds the full Sprint 1 DQ runner defined in the project brief.
"""

from __future__ import annotations

import csv
import logging
import os
import re
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / os.getenv("OUTPUT_DIR", "output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class ValidationIssue:
	rule_id: str
	severity: str
	entity: str
	message: str


@dataclass(frozen=True)
class DQViolation:
	rule_id: str
	severity: str
	table: str
	company_id: Optional[str]
	year: Optional[str]
	field_name: str
	issue: str
	raw_value: str = ""


def _load(conn: sqlite3.Connection, table: str) -> pd.DataFrame:
	return pd.read_sql_query(f"SELECT * FROM {table}", conn)


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
	"""Write validation failures to the CSV expected by the helper tests."""

	output_path.parent.mkdir(parents=True, exist_ok=True)
	with output_path.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=["rule_id", "severity", "entity", "message"])
		writer.writeheader()
		writer.writerows(asdict(issue) for issue in issues)


def _write_dq_failures(violations: list[DQViolation], output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with output_path.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(
			handle,
			fieldnames=["rule_id", "severity", "table", "company_id", "year", "field_name", "issue", "raw_value"],
		)
		writer.writeheader()
		writer.writerows(asdict(violation) for violation in violations)


def dq01_pk_uniqueness(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-01: companies.id must be unique."""

	df = _load(conn, "companies")
	dupes = df[df.duplicated(subset=["id"], keep=False)]
	return [
		DQViolation("DQ-01", "CRITICAL", "companies", str(row["id"]), None, "id", f"Duplicate primary key: '{row['id']}'", str(row["id"]))
		for _, row in dupes.iterrows()
	]


def dq02_annual_pk_uniqueness(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-02: (company_id, year) must be unique in annual financial tables."""

	violations: list[DQViolation] = []
	for table in ["profitandloss", "balancesheet", "cashflow", "financial_ratios", "market_cap"]:
		df = _load(conn, table)
		dupes = df[df.duplicated(subset=["company_id", "year"], keep=False)]
		for _, row in dupes.iterrows():
			violations.append(
				DQViolation(
					"DQ-02",
					"CRITICAL",
					table,
					str(row.get("company_id")),
					str(row.get("year")),
					"company_id/year",
					"Duplicate composite primary key",
					f"{row.get('company_id')} | {row.get('year')}",
				)
			)
	return violations


def dq03_fk_integrity(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-03: All company_id values in child tables must exist in companies.id."""

	violations: list[DQViolation] = []
	parent_ids = set(pd.read_sql_query("SELECT id FROM companies", conn)["id"].astype(str).tolist())
	child_tables = [
		"profitandloss",
		"balancesheet",
		"cashflow",
		"analysis",
		"documents",
		"prosandcons",
		"sectors",
		"stock_prices",
		"market_cap",
		"financial_ratios",
		"peer_groups",
	]

	for table in child_tables:
		df = _load(conn, table)
		if "company_id" not in df.columns:
			continue
		orphans = df[~df["company_id"].astype(str).isin(parent_ids)]
		for _, row in orphans.iterrows():
			violations.append(
				DQViolation(
					"DQ-03",
					"CRITICAL",
					table,
					str(row.get("company_id")),
					str(row.get("year") if "year" in row else row.get("Year")),
					"company_id",
					f"Orphan FK: '{row.get('company_id')}' not in companies",
					str(row.get("company_id")),
				)
			)
	return violations


def dq04_balance_sheet_balance(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-04: balance sheets should be close to balanced."""

	violations: list[DQViolation] = []
	df = _load(conn, "balancesheet")
	for _, row in df.iterrows():
		try:
			total_assets = float(row["total_assets"])
			total_liabilities = float(row["total_liabilities"])
			if total_assets == 0:
				continue
			if abs(total_assets - total_liabilities) / abs(total_assets) >= 0.01:
				violations.append(
					DQViolation(
						"DQ-04",
						"WARNING",
						"balancesheet",
						str(row.get("company_id")),
						str(row.get("year")),
						"total_assets/total_liabilities",
						f"Balance mismatch: assets={total_assets}, liabilities={total_liabilities}",
						f"{total_assets} vs {total_liabilities}",
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq05_opm_crosscheck(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-05: operating profit margin should align with sales and operating profit."""

	violations: list[DQViolation] = []
	df = _load(conn, "profitandloss")
	for _, row in df.iterrows():
		try:
			opm_src = float(row["opm_percentage"])
			sales = float(row["sales"])
			op_profit = float(row["operating_profit"])
			if sales == 0:
				continue
			opm_computed = (op_profit / sales) * 100
			if abs(opm_src - opm_computed) > 1.0:
				violations.append(
					DQViolation(
						"DQ-05",
						"WARNING",
						"profitandloss",
						str(row.get("company_id")),
						str(row.get("year")),
						"opm_percentage",
						f"OPM mismatch: source={opm_src:.2f}%, computed={opm_computed:.2f}%",
						str(opm_src),
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq06_positive_sales(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-06: sales should be positive outside the financial sector."""

	violations: list[DQViolation] = []
	df = _load(conn, "profitandloss")
	financial_ids: set[str] = set()
	try:
		sectors_df = _load(conn, "sectors")
		financial_ids = set(
			sectors_df[sectors_df["broad_sector"].astype(str).str.contains("Financial", case=False, na=False)]["company_id"].astype(str).tolist()
		)
	except Exception:
		pass

	for _, row in df.iterrows():
		if str(row.get("company_id")) in financial_ids:
			continue
		try:
			if float(row["sales"]) <= 0:
				violations.append(
					DQViolation(
						"DQ-06",
						"WARNING",
						"profitandloss",
						str(row.get("company_id")),
						str(row.get("year")),
						"sales",
						f"Non-positive sales: {row['sales']}",
						str(row.get("sales")),
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq07_year_format(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-07: all year values in annual tables should match YYYY-MM."""

	violations: list[DQViolation] = []
	pattern = re.compile(r"^\d{4}-\d{2}$")
	for table in ["profitandloss", "balancesheet", "cashflow", "financial_ratios"]:
		df = _load(conn, table)
		bad = df[~df["year"].astype(str).apply(lambda value: bool(pattern.match(value)))]
		for _, row in bad.iterrows():
			violations.append(
				DQViolation(
					"DQ-07",
					"CRITICAL",
					table,
					str(row.get("company_id")),
					str(row.get("year")),
					"year",
					f"Invalid year format: '{row.get('year')}'",
					str(row.get("year")),
				)
			)
	return violations


def dq08_ticker_format(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-08: company_id must be 2-12 chars and uppercase after normalisation."""

	violations: list[DQViolation] = []
	for table in ["profitandloss", "balancesheet", "cashflow", "analysis", "documents", "prosandcons", "sectors", "stock_prices", "market_cap", "financial_ratios", "peer_groups"]:
		df = _load(conn, table)
		if "company_id" not in df.columns:
			continue
		values = df["company_id"].fillna("").astype(str).str.strip()
		bad = df[(values.str.len() < 2) | (values.str.len() > 12) | (values != values.str.upper())]
		for _, row in bad.iterrows():
			violations.append(
				DQViolation(
					"DQ-08",
					"CRITICAL",
					table,
					str(row.get("company_id")),
					str(row.get("year") if "year" in row else row.get("Year")),
					"company_id",
					f"Bad ticker format: '{row.get('company_id')}'",
					str(row.get("company_id")),
				)
			)
	return violations


def dq09_net_cash_check(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-09: net cash flow should match the component cash flows."""

	violations: list[DQViolation] = []
	df = _load(conn, "cashflow")
	for _, row in df.iterrows():
		try:
			cfo = float(row.get("operating_activity", 0) or 0)
			cfi = float(row.get("investing_activity", 0) or 0)
			cff = float(row.get("financing_activity", 0) or 0)
			net = float(row.get("net_cash_flow", 0) or 0)
			computed = cfo + cfi + cff
			if abs(net - computed) > 10:
				violations.append(
					DQViolation(
						"DQ-09",
						"WARNING",
						"cashflow",
						str(row.get("company_id")),
						str(row.get("year")),
						"net_cash_flow",
						f"Net cash mismatch: stored={net:.0f}, computed={computed:.0f}, diff={abs(net - computed):.0f}",
						str(net),
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq10_nonneg_fixed_assets(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-10: fixed assets should be non-negative."""

	violations: list[DQViolation] = []
	df = _load(conn, "balancesheet")
	for _, row in df.iterrows():
		try:
			fixed_assets = float(row.get("fixed_assets", 0) or 0)
			if fixed_assets < 0:
				violations.append(
					DQViolation(
						"DQ-10",
						"WARNING",
						"balancesheet",
						str(row.get("company_id")),
						str(row.get("year")),
						"fixed_assets",
						f"Negative fixed_assets: {fixed_assets}",
						str(fixed_assets),
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq11_tax_rate_range(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-11: tax_percentage should be between 0 and 60."""

	violations: list[DQViolation] = []
	df = _load(conn, "profitandloss")
	for _, row in df.iterrows():
		try:
			tax = float(row.get("tax_percentage", 25) or 25)
			if not (0 <= tax <= 60):
				violations.append(
					DQViolation(
						"DQ-11",
						"WARNING",
						"profitandloss",
						str(row.get("company_id")),
						str(row.get("year")),
						"tax_percentage",
						f"Tax rate out of range: {tax}%",
						str(tax),
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq12_dividend_payout_cap(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-12: dividend payout should not exceed 200 percent."""

	violations: list[DQViolation] = []
	df = _load(conn, "profitandloss")
	for _, row in df.iterrows():
		try:
			dp = float(row.get("dividend_payout", 0) or 0)
			if dp > 200:
				violations.append(
					DQViolation(
						"DQ-12",
						"WARNING",
						"profitandloss",
						str(row.get("company_id")),
						str(row.get("year")),
						"dividend_payout",
						f"Dividend payout > 200%: {dp}%",
						str(dp),
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq13_url_validity(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-13: annual report URLs should be reachable where possible."""

	violations: list[DQViolation] = []
	df = _load(conn, "documents")
	if "Annual_Report" not in df.columns:
		return violations

	sample = df[df["Annual_Report"].notna()].head(20)
	for _, row in sample.iterrows():
		url = str(row["Annual_Report"]).strip()
		if not url.startswith("http"):
			continue
		try:
			response = requests.head(url, timeout=5, allow_redirects=True)
			if response.status_code != 200:
				violations.append(
					DQViolation(
						"DQ-13",
						"WARNING",
						"documents",
						str(row.get("company_id")),
						str(row.get("Year")),
						"Annual_Report",
						f"URL returned HTTP {response.status_code}",
						url,
					)
				)
		except requests.RequestException as exc:
			violations.append(
				DQViolation(
					"DQ-13",
					"WARNING",
					"documents",
					str(row.get("company_id")),
					str(row.get("Year")),
					"Annual_Report",
					f"URL request failed: {exc}",
					url,
				)
			)
	return violations


def dq14_eps_sign_consistency(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-14: positive profits should have positive EPS."""

	violations: list[DQViolation] = []
	df = _load(conn, "profitandloss")
	for _, row in df.iterrows():
		try:
			eps = float(row.get("eps", 0) or 0)
			net = float(row.get("net_profit", 0) or 0)
			if net > 0 and eps <= 0:
				violations.append(
					DQViolation(
						"DQ-14",
						"WARNING",
						"profitandloss",
						str(row.get("company_id")),
						str(row.get("year")),
						"eps",
						f"net_profit={net:.0f} > 0 but eps={eps}",
						str(eps),
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq15_bs_strict_balance(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-15: record strict balance mismatches as informational rows."""

	violations: list[DQViolation] = []
	df = _load(conn, "balancesheet")
	for _, row in df.iterrows():
		try:
			total_assets = float(row["total_assets"])
			total_liabilities = float(row["total_liabilities"])
			if total_assets != total_liabilities:
				violations.append(
					DQViolation(
						"DQ-15",
						"INFO",
						"balancesheet",
						str(row.get("company_id")),
						str(row.get("year")),
						"total_assets/total_liabilities",
						f"Strict mismatch: {total_assets} != {total_liabilities}",
						f"{total_assets} vs {total_liabilities}",
					)
				)
		except (TypeError, ValueError):
			pass
	return violations


def dq16_coverage_check(conn: sqlite3.Connection) -> list[DQViolation]:
	"""DQ-16: each company should have at least five annual financial records."""

	violations: list[DQViolation] = []
	companies = pd.read_sql_query("SELECT id FROM companies", conn)["id"].astype(str).tolist()
	for table in ["profitandloss", "balancesheet", "cashflow"]:
		df = pd.read_sql_query(f"SELECT company_id, COUNT(*) AS yr_count FROM {table} GROUP BY company_id", conn)
		count_map = dict(zip(df["company_id"].astype(str), df["yr_count"]))
		for company_id in companies:
			count = int(count_map.get(company_id, 0))
			if count < 5:
				violations.append(
					DQViolation(
						"DQ-16",
						"WARNING",
						table,
						company_id,
						None,
						"year",
						f"Only {count} years of data (minimum 5 required)",
						str(count),
					)
				)
	return violations


DQ_RULES = [
	dq01_pk_uniqueness,
	dq02_annual_pk_uniqueness,
	dq03_fk_integrity,
	dq04_balance_sheet_balance,
	dq05_opm_crosscheck,
	dq06_positive_sales,
	dq07_year_format,
	dq08_ticker_format,
	dq09_net_cash_check,
	dq10_nonneg_fixed_assets,
	dq11_tax_rate_range,
	dq12_dividend_payout_cap,
	dq13_url_validity,
	dq14_eps_sign_consistency,
	dq15_bs_strict_balance,
	dq16_coverage_check,
]


def run_all_rules(conn: sqlite3.Connection) -> list[DQViolation]:
	"""Run all 16 DQ rules and collect violations."""

	all_violations: list[DQViolation] = []
	for rule_fn in DQ_RULES:
		logger.info("Running %s ...", rule_fn.__name__)
		try:
			violations = rule_fn(conn)
			all_violations.extend(violations)
			if violations:
				logger.warning("  %d violation(s)", len(violations))
			else:
				logger.info("  Clean")
		except Exception as exc:
			logger.exception("  Rule function failed: %s", exc)
	return all_violations


def write_violations(violations: list[DQViolation]) -> None:
	"""Write all DQ violations to output/validation_failures.csv."""

	path = OUTPUT_DIR / "validation_failures.csv"
	_write_dq_failures(violations, path)
	logger.info("%d violations written -> %s", len(violations), path)


def main() -> None:
	"""Run the full DQ suite against the configured SQLite database."""

	logging.basicConfig(level=logging.INFO)
	db_path = Path(os.getenv("DB_PATH", str(ROOT_DIR / "data" / "nifty100.db")))
	if not db_path.is_absolute():
		db_path = ROOT_DIR / db_path

	with sqlite3.connect(db_path) as conn:
		violations = run_all_rules(conn)

	write_violations(violations)

	critical = [violation for violation in violations if violation.severity == "CRITICAL"]
	warnings = [violation for violation in violations if violation.severity == "WARNING"]
	infos = [violation for violation in violations if violation.severity == "INFO"]

	print(f"\n{'=' * 50}")
	print(f"DQ Summary: CRITICAL={len(critical)} | WARNING={len(warnings)} | INFO={len(infos)}")
	print(f"{'=' * 50}\n")

	if critical:
		print("CRITICAL violations must be resolved before Sprint 2!")
		for violation in critical:
			print(f"[{violation.rule_id}] {violation.table}.{violation.field_name} - {violation.issue}")
		raise SystemExit(1)

	print("No CRITICAL violations. Sprint 1 DQ gate passed!")


if __name__ == "__main__":
	raise SystemExit(main())

