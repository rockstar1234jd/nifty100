"""Sprint 2 ratio engine for the Nifty 100 project."""

from __future__ import annotations

import csv
import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = Path(os.getenv("DB_PATH", str(ROOT_DIR / "data" / "nifty100.db")))
DEFAULT_OUTPUT_DIR = ROOT_DIR / "output"

SPRINT2_COLUMNS: dict[str, str] = {
	"net_profit_margin_pct": "REAL",
	"operating_profit_margin_pct": "REAL",
	"return_on_capital_employed_pct": "REAL",
	"return_on_assets_pct": "REAL",
	"ebit_cr": "REAL",
	"opm_crosscheck_flag": "INTEGER",
	"high_leverage_flag": "INTEGER",
	"icr_label": "TEXT",
	"icr_risk_flag": "INTEGER",
	"net_debt_cr": "REAL",
	"revenue_cagr_3yr": "REAL",
	"revenue_cagr_3yr_flag": "TEXT",
	"revenue_cagr_5yr": "REAL",
	"revenue_cagr_5yr_flag": "TEXT",
	"revenue_cagr_10yr": "REAL",
	"revenue_cagr_10yr_flag": "TEXT",
	"pat_cagr_3yr": "REAL",
	"pat_cagr_3yr_flag": "TEXT",
	"pat_cagr_5yr": "REAL",
	"pat_cagr_5yr_flag": "TEXT",
	"pat_cagr_10yr": "REAL",
	"pat_cagr_10yr_flag": "TEXT",
	"eps_cagr_3yr": "REAL",
	"eps_cagr_3yr_flag": "TEXT",
	"eps_cagr_5yr": "REAL",
	"eps_cagr_5yr_flag": "TEXT",
	"eps_cagr_10yr": "REAL",
	"eps_cagr_10yr_flag": "TEXT",
	"cfo_quality_score": "REAL",
	"cfo_quality_label": "TEXT",
	"capex_intensity_pct": "REAL",
	"capex_intensity_label": "TEXT",
	"fcf_conversion_pct": "REAL",
	"capital_allocation_pattern": "TEXT",
	"composite_quality_score": "REAL",
}


def net_profit_margin(net_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
	if net_profit is None or sales is None or sales == 0:
		return None
	return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
	if operating_profit is None or sales is None or sales == 0:
		return None
	return round((operating_profit / sales) * 100, 2)


def opm_crosscheck_flag(opm_computed: Optional[float], opm_source: Optional[float], tolerance_pp: float = 1.0) -> bool:
	if opm_computed is None or opm_source is None:
		return False
	return abs(opm_computed - opm_source) > tolerance_pp


def ebit(operating_profit: Optional[float], depreciation: Optional[float]) -> Optional[float]:
	if operating_profit is None:
		return None
	return round(operating_profit - (depreciation or 0.0), 2)


def return_on_equity(net_profit: Optional[float], equity_capital: Optional[float], reserves: Optional[float]) -> Optional[float]:
	if net_profit is None or equity_capital is None or reserves is None:
		return None
	equity = equity_capital + reserves
	if equity <= 0:
		return None
	return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(
	ebit_value: Optional[float],
	equity_capital: Optional[float],
	reserves: Optional[float],
	borrowings: Optional[float],
) -> Optional[float]:
	if None in (ebit_value, equity_capital, reserves, borrowings):
		return None
	capital_employed = equity_capital + reserves + borrowings
	if capital_employed <= 0:
		return None
	return round((ebit_value / capital_employed) * 100, 2)


def return_on_assets(net_profit: Optional[float], total_assets: Optional[float]) -> Optional[float]:
	if net_profit is None or total_assets is None or total_assets == 0:
		return None
	return round((net_profit / total_assets) * 100, 2)


def debt_to_equity(borrowings: Optional[float], equity_capital: Optional[float], reserves: Optional[float]) -> Optional[float]:
	if borrowings is None or equity_capital is None or reserves is None:
		return None
	if borrowings == 0:
		return 0.0
	equity = equity_capital + reserves
	if equity <= 0:
		return None
	return round(borrowings / equity, 2)


def high_leverage_flag(de_ratio: Optional[float], is_financial_sector: bool) -> bool:
	if de_ratio is None or is_financial_sector:
		return False
	return de_ratio > 5.0


def interest_coverage(operating_profit: Optional[float], other_income: Optional[float], interest: Optional[float]) -> Optional[float]:
	if operating_profit is None or interest is None or interest == 0:
		return None
	return round((operating_profit + (other_income or 0.0)) / interest, 2)


def icr_label(interest: Optional[float]) -> str:
	return "Debt Free" if interest is None or interest == 0 else "Computed"


def icr_risk_flag(icr: Optional[float]) -> bool:
	if icr is None:
		return False
	return icr < 1.5


def net_debt(borrowings: Optional[float], investments: Optional[float]) -> Optional[float]:
	if borrowings is None:
		return None
	return round(borrowings - (investments or 0.0), 2)


def asset_turnover(sales: Optional[float], total_assets: Optional[float]) -> Optional[float]:
	if sales is None or total_assets is None or total_assets == 0:
		return None
	return round(sales / total_assets, 2)


def book_value_per_share(equity_capital: Optional[float], reserves: Optional[float], face_value: Optional[float]) -> Optional[float]:
	if equity_capital is None or reserves is None or not face_value:
		return None
	shares = equity_capital / face_value
	if shares == 0:
		return None
	return round((equity_capital + reserves) / shares, 2)


def cagr(start: Optional[float], end: Optional[float], n: int) -> tuple[Optional[float], Optional[str]]:
	if start is None or end is None:
		return None, "INSUFFICIENT"
	if start == 0:
		return None, "ZERO_BASE"
	if start > 0 and end > 0:
		return round((((end / start) ** (1.0 / n)) - 1) * 100, 2), None
	if start > 0 and end <= 0:
		return None, "DECLINE_TO_LOSS"
	if start < 0 and end > 0:
		return None, "TURNAROUND"
	return None, "BOTH_NEGATIVE"


def _shift_year(year_str: str, delta: int) -> str:
	yyyy, mm = year_str.split("-")
	return f"{int(yyyy) + delta:04d}-{mm}"


def windowed_cagr(series: dict[str, Optional[float]], end_year: str, n: int) -> tuple[Optional[float], Optional[str]]:
	base_year = _shift_year(end_year, -n)
	if end_year not in series or base_year not in series:
		return None, "INSUFFICIENT"
	return cagr(series.get(base_year), series.get(end_year), n)


def compute_growth_metrics(
	revenue_series: dict[str, Optional[float]],
	pat_series: dict[str, Optional[float]],
	eps_series: dict[str, Optional[float]],
	end_year: str,
) -> dict[str, Optional[float | str]]:
	result: dict[str, Optional[float | str]] = {}
	for label, series in (("revenue", revenue_series), ("pat", pat_series), ("eps", eps_series)):
		for window in (3, 5, 10):
			value, flag = windowed_cagr(series, end_year, window)
			result[f"{label}_cagr_{window}yr"] = value
			result[f"{label}_cagr_{window}yr_flag"] = flag
	return result


def free_cash_flow(operating_activity: Optional[float], investing_activity: Optional[float]) -> Optional[float]:
	if operating_activity is None:
		return None
	return round(operating_activity + (investing_activity or 0.0), 2)


def cfo_quality_score(pairs: list[tuple[Optional[float], Optional[float]]]) -> tuple[Optional[float], Optional[str]]:
	ratios: list[float] = []
	for cfo, pat in pairs:
		if cfo is None or pat is None or pat == 0:
			continue
		ratios.append(cfo / pat)
	if not ratios:
		return None, None
	avg = sum(ratios) / len(ratios)
	return round(avg, 2), ("Accrual Risk" if avg < 1 else "Cash-Backed")


def capex_intensity(investing_activity: Optional[float], sales: Optional[float]) -> tuple[Optional[float], Optional[str]]:
	if investing_activity is None or sales is None or sales == 0:
		return None, None
	capex = abs(investing_activity)
	value = round((capex / sales) * 100, 2)
	if value >= 15:
		label = "Capital Intensive"
	elif value <= 5:
		label = "Asset Light"
	else:
		label = "Moderate"
	return value, label


def fcf_conversion_rate(free_cash_flow_value: Optional[float], operating_profit: Optional[float]) -> Optional[float]:
	if free_cash_flow_value is None or operating_profit is None or operating_profit == 0:
		return None
	return round((free_cash_flow_value / operating_profit) * 100, 2)


def _sign(value: Optional[float]) -> str:
	if value is None:
		return "N"
	return "P" if value >= 0 else "N"


def capital_allocation_pattern(
	operating_activity: Optional[float],
	investing_activity: Optional[float],
	financing_activity: Optional[float],
	dividend_payout: Optional[float],
) -> tuple[str, str, str, str]:
	pattern = f"{_sign(operating_activity)}{_sign(investing_activity)}{_sign(financing_activity)}"
	if pattern == "PPN" and (dividend_payout or 0) > 0:
		label = "Reinvestor"
	elif pattern in {"PPN", "PNN", "PPP"}:
		label = "Growth"
	else:
		label = "Mixed"
	return label, _sign(operating_activity), _sign(investing_activity), _sign(financing_activity)


def write_capital_allocation_csv(records: list[dict], output_path: Path | None = None) -> Path:
	path = output_path or (DEFAULT_OUTPUT_DIR / "capital_allocation.csv")
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"])
		writer.writeheader()
		writer.writerows(records)
	return path


def compute_row_ratios(pl: dict, bs: dict, is_financial: bool) -> dict[str, Optional[float | str | int]]:
	opm_value = operating_profit_margin(pl.get("operating_profit"), pl.get("sales"))
	ebit_value = ebit(pl.get("operating_profit"), pl.get("depreciation"))
	de_ratio = debt_to_equity(bs.get("borrowings"), bs.get("equity_capital"), bs.get("reserves"))
	icr_value = interest_coverage(pl.get("operating_profit"), pl.get("other_income"), pl.get("interest"))
	return {
		"net_profit_margin_pct": net_profit_margin(pl.get("net_profit"), pl.get("sales")),
		"operating_profit_margin_pct": opm_value,
		"return_on_equity_pct": return_on_equity(pl.get("net_profit"), bs.get("equity_capital"), bs.get("reserves")),
		"return_on_capital_employed_pct": return_on_capital_employed(ebit_value, bs.get("equity_capital"), bs.get("reserves"), bs.get("borrowings")),
		"return_on_assets_pct": return_on_assets(pl.get("net_profit"), bs.get("total_assets")),
		"ebit_cr": ebit_value,
		"debt_to_equity": de_ratio,
		"interest_coverage": icr_value,
		"opm_crosscheck_flag": int(opm_crosscheck_flag(opm_value, pl.get("opm_percentage"))),
		"high_leverage_flag": int(high_leverage_flag(de_ratio, is_financial)),
		"icr_label": icr_label(pl.get("interest")),
		"icr_risk_flag": int(icr_risk_flag(icr_value)),
		"net_debt_cr": net_debt(bs.get("borrowings"), bs.get("investments")),
		"asset_turnover": asset_turnover(pl.get("sales"), bs.get("total_assets")),
		"earnings_per_share": pl.get("eps"),
		"book_value_per_share": book_value_per_share(bs.get("equity_capital"), bs.get("reserves"), pl.get("_face_value")),
		"dividend_payout_ratio_pct": pl.get("dividend_payout"),
		"total_debt_cr": bs.get("borrowings"),
	}


def _migrate_schema(conn: sqlite3.Connection) -> None:
	existing = {row[1] for row in conn.execute("PRAGMA table_info(financial_ratios)").fetchall()}
	added = 0
	for column, column_type in SPRINT2_COLUMNS.items():
		if column not in existing:
			conn.execute(f"ALTER TABLE financial_ratios ADD COLUMN {column} {column_type}")
			added += 1
	conn.commit()
	if added:
		logger.info("Schema migration: %d new column(s) added to financial_ratios", added)
	else:
		logger.info("Schema migration: all Sprint 2 columns already present")


def _latest_company_rows(frame: pd.DataFrame) -> pd.DataFrame:
	return frame.assign(year=frame["year"].astype(str)).sort_values(["company_id", "year"]).groupby("company_id", as_index=False).tail(1)


def _cross_check_source_values(conn: sqlite3.Connection, companies_df: pd.DataFrame, log_path: str = "output/ratio_edge_cases.log") -> None:
	financial_ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
	if financial_ratios.empty:
		Path(log_path).parent.mkdir(parents=True, exist_ok=True)
		Path(log_path).write_text("No financial ratios available.\n", encoding="utf-8")
		return
	latest = _latest_company_rows(financial_ratios)
	merged = latest.merge(companies_df, left_on="company_id", right_on="id", how="left")
	lines = [
		"=" * 70,
		"RATIO ENGINE - SOURCE CROSS-CHECK LOG",
		f"Run against {len(merged)} companies - latest year per company",
		"=" * 70,
		"",
	]
	anomalies = 0
	for _, row in merged.iterrows():
		company_id = row.get("company_id")
		roce_engine = row.get("return_on_capital_employed_pct")
		roce_source = row.get("roce_percentage")
		if pd.notna(roce_engine) and pd.notna(roce_source) and abs(roce_engine - roce_source) > 5:
			lines.append(f"[{company_id}] ROCE engine={roce_engine:.2f}% source={roce_source:.2f}% diff={abs(roce_engine - roce_source):.2f}pp")
			anomalies += 1
		roe_engine = row.get("return_on_equity_pct")
		roe_source = row.get("roe_percentage")
		if pd.notna(roe_engine) and pd.notna(roe_source):
			if roe_source < 1 and roe_engine > 5:
				lines.append(f"[{company_id}] ROE engine={roe_engine:.2f}% source={roe_source} (source looks like decimal-fraction bug)")
				anomalies += 1
			elif abs(roe_engine - roe_source) > 5:
				lines.append(f"[{company_id}] ROE engine={roe_engine:.2f}% source={roe_source:.2f}% diff={abs(roe_engine - roe_source):.2f}pp")
				anomalies += 1
	lines.extend(["", f"Total anomalies: {anomalies}", "=" * 70])
	path = Path(log_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text("\n".join(lines), encoding="utf-8")


def _composite_quality_score(frame: pd.DataFrame) -> pd.Series:
	"""Simple bounded score used for the Sprint 2 population output."""
	if frame.empty:
		return pd.Series(dtype=float)

	def _scale(series: pd.Series, invert: bool = False) -> pd.Series:
		filled = series.fillna(series.median())
		if filled.empty:
			return pd.Series(dtype=float)
		p10 = filled.quantile(0.10)
		p90 = filled.quantile(0.90)
		if pd.isna(p10) or pd.isna(p90) or p90 == p10:
			return pd.Series(50.0, index=series.index)
		clipped = filled.clip(p10, p90)
		scaled = (clipped - p10) / (p90 - p10) * 100
		return (100 - scaled).round(2) if invert else scaled.round(2)

	roe = _scale(frame.get("return_on_equity_pct", pd.Series(index=frame.index, dtype=float)))
	fcf = _scale(frame.get("free_cash_flow_cr", pd.Series(index=frame.index, dtype=float)))
	roce = _scale(frame.get("return_on_capital_employed_pct", pd.Series(index=frame.index, dtype=float)))
	de = _scale(frame.get("debt_to_equity", pd.Series(index=frame.index, dtype=float)), invert=True)
	return (0.30 * roe + 0.25 * fcf + 0.25 * roce + 0.20 * de).clip(0, 100).round(2)


def main() -> None:
	"""Populate the SQLite ``financial_ratios`` table from the source tables."""
	if not DEFAULT_DB_PATH.exists():
		raise FileNotFoundError(f"Database not found: {DEFAULT_DB_PATH}")

	with sqlite3.connect(DEFAULT_DB_PATH) as conn:
		conn.execute("PRAGMA foreign_keys = ON")
		_migrate_schema(conn)

		companies = pd.read_sql_query("SELECT id, face_value, roce_percentage, roe_percentage FROM companies", conn)
		sectors = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
		pl_all = pd.read_sql_query("SELECT * FROM profitandloss ORDER BY company_id, year", conn)
		bs_all = pd.read_sql_query("SELECT * FROM balancesheet ORDER BY company_id, year", conn)
		cf_all = pd.read_sql_query("SELECT * FROM cashflow ORDER BY company_id, year", conn)

		financial_ids = set(sectors.loc[sectors["broad_sector"].astype(str).str.contains("Financial", case=False, na=False), "company_id"].astype(str))
		rows: list[dict] = []
		capital_allocation_rows: list[dict] = []

		for _, company in companies.iterrows():
			company_id = company["id"]
			is_financial = company_id in financial_ids
			face_value = company["face_value"]
			pl_co = pl_all[pl_all["company_id"] == company_id].set_index("year")
			bs_co = bs_all[bs_all["company_id"] == company_id].set_index("year")
			cf_co = cf_all[cf_all["company_id"] == company_id].set_index("year")

			revenue_series = pl_co["sales"].dropna().to_dict()
			pat_series = pl_co["net_profit"].dropna().to_dict()
			eps_series = pl_co["eps"].dropna().to_dict()

			for year in sorted(set(pl_co.index) & set(bs_co.index)):
				pl_row = pl_co.loc[year].to_dict()
				pl_row["_face_value"] = face_value
				bs_row = bs_co.loc[year].to_dict()
				row = compute_row_ratios(pl_row, bs_row, is_financial)
				row["company_id"] = company_id
				row["year"] = year

				if year in cf_co.index:
					cf_row = cf_co.loc[year].to_dict()
					operating_activity = cf_row.get("operating_activity")
					investing_activity = cf_row.get("investing_activity")
					financing_activity = cf_row.get("financing_activity")
					free_cash_flow_value = free_cash_flow(operating_activity, investing_activity)
					row["free_cash_flow_cr"] = free_cash_flow_value
					row["cash_from_operations_cr"] = operating_activity
					row["capex_cr"] = abs(investing_activity) if investing_activity is not None else None
					capex_value, capex_label = capex_intensity(investing_activity, pl_row.get("sales"))
					row["capex_intensity_pct"] = capex_value
					row["capex_intensity_label"] = capex_label
					row["fcf_conversion_pct"] = fcf_conversion_rate(free_cash_flow_value, pl_row.get("operating_profit"))
					pattern_label, cfo_sign, cfi_sign, cff_sign = capital_allocation_pattern(operating_activity, investing_activity, financing_activity, pl_row.get("dividend_payout"))
					row["capital_allocation_pattern"] = pattern_label
					capital_allocation_rows.append({
						"company_id": company_id,
						"year": year,
						"cfo_sign": cfo_sign,
						"cfi_sign": cfi_sign,
						"cff_sign": cff_sign,
						"pattern_label": pattern_label,
					})
				else:
					for column in ("free_cash_flow_cr", "cash_from_operations_cr", "capex_cr", "capex_intensity_pct", "capex_intensity_label", "fcf_conversion_pct", "capital_allocation_pattern"):
						row[column] = None

				trailing_years = [year_key for year_key in sorted(cf_co.index) if year_key <= year][-5:]
				pairs = [
					(cf_co.at[year_key, "operating_activity"] if year_key in cf_co.index else None, pl_co.at[year_key, "net_profit"] if year_key in pl_co.index else None)
					for year_key in trailing_years
				]
				q_score, q_label = cfo_quality_score(pairs)
				row["cfo_quality_score"] = q_score
				row["cfo_quality_label"] = q_label
				row.update(compute_growth_metrics(revenue_series, pat_series, eps_series, year))
				rows.append(row)

		financial_ratios = pd.DataFrame(rows)
		if not financial_ratios.empty:
			financial_ratios["composite_quality_score"] = _composite_quality_score(financial_ratios)

		for column in SPRINT2_COLUMNS:
			if column not in financial_ratios.columns:
				financial_ratios[column] = None

		financial_ratios = financial_ratios[[column for column in financial_ratios.columns if column in {"company_id", "year", *SPRINT2_COLUMNS.keys(), "net_profit_margin_pct", "operating_profit_margin_pct", "debt_to_equity", "interest_coverage", "asset_turnover", "free_cash_flow_cr", "earnings_per_share", "book_value_per_share", "dividend_payout_ratio_pct", "total_debt_cr", "cash_from_operations_cr", "capex_cr"}]]
		conn.execute("DELETE FROM financial_ratios")
		conn.commit()
		financial_ratios.to_sql("financial_ratios", conn, if_exists="append", index=False)
		conn.commit()

		write_capital_allocation_csv(capital_allocation_rows)
		_cross_check_source_values(conn, companies)

	print(f"financial_ratios populated: {len(financial_ratios)} rows")


if __name__ == "__main__":
	main()