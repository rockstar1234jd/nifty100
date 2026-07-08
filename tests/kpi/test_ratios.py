import pytest

from src.analytics.ratios import (
	asset_turnover,
	book_value_per_share,
	cagr,
	capital_allocation_pattern,
	compute_growth_metrics,
	compute_row_ratios,
	debt_to_equity,
	fcf_conversion_rate,
	free_cash_flow,
	high_leverage_flag,
	icr_label,
	icr_risk_flag,
	interest_coverage,
	net_debt,
	net_profit_margin,
	operating_profit_margin,
	return_on_assets,
	return_on_capital_employed,
	return_on_equity,
	windowed_cagr,
)


def test_profitability_ratios_handle_basic_cases() -> None:
	assert net_profit_margin(150, 1000) == 15.0
	assert operating_profit_margin(210, 1000) == 21.0
	assert return_on_equity(100, 50, 450) == 20.0
	assert return_on_capital_employed(150, 50, 450, 500) == 15.0
	assert return_on_assets(100, 2000) == 5.0


def test_leverage_ratios_handle_edge_cases() -> None:
	assert debt_to_equity(0, 50, 450) == 0.0
	assert debt_to_equity(500, 50, 450) == 1.0
	assert debt_to_equity(100, 50, -100) is None
	assert high_leverage_flag(6.0, False) is True
	assert high_leverage_flag(8.0, True) is False


def test_interest_coverage_helpers() -> None:
	assert interest_coverage(100, 20, 10) == 12.0
	assert interest_coverage(100, 20, 0) is None
	assert icr_label(0) == "Debt Free"
	assert icr_label(50) == "Computed"
	assert icr_risk_flag(1.0) is True
	assert icr_risk_flag(None) is False


def test_efficiency_and_cashflow_helpers() -> None:
	assert net_debt(0, 500) == -500.0
	assert asset_turnover(1000, 500) == 2.0
	assert book_value_per_share(50, 450, 10) == 100.0
	assert free_cash_flow(100, -20) == 80.0
	assert fcf_conversion_rate(80, 40) == 200.0
	assert capital_allocation_pattern(100, -20, -30, 5)[0] in {"Reinvestor", "Growth", "Mixed"}


def test_cagr_helpers() -> None:
	value, flag = cagr(100, 133.1, 3)
	assert value == pytest.approx(10.0, abs=0.01)
	assert flag is None
	assert windowed_cagr({"2019-03": 100.0, "2024-03": 161.051}, "2024-03", 5)[0] == pytest.approx(10.0, abs=0.01)
	metrics = compute_growth_metrics(
		{"2019-03": 100.0, "2024-03": 161.051},
		{"2019-03": 50.0, "2024-03": 80.5},
		{"2019-03": 5.0, "2024-03": 8.05},
		"2024-03",
	)
	assert len(metrics) == 18


def test_compute_row_ratios_returns_expected_fields() -> None:
	row = compute_row_ratios(
		{"sales": 1000, "operating_profit": 200, "other_income": 20, "interest": 10, "depreciation": 20, "net_profit": 100, "opm_percentage": 21, "eps": 5, "dividend_payout": 10, "_face_value": 10},
		{"equity_capital": 50, "reserves": 450, "borrowings": 500, "investments": 100, "total_assets": 2000},
		False,
	)
	assert row["net_profit_margin_pct"] == 10.0
	assert row["debt_to_equity"] == 1.0
	assert row["book_value_per_share"] == 100.0