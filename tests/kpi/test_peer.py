import pandas as pd

from src.analytics.peer import PEER_METRICS, compute_peer_percentiles, load_peer_base_frame


def test_peer_base_frame_has_expected_columns() -> None:
	frame = load_peer_base_frame()
	assert not frame.empty
	for column in ["company_id", "company_name", "peer_group_name", *PEER_METRICS]:
		assert column in frame.columns


def test_peer_percentiles_invert_debt_to_equity() -> None:
	frame = pd.DataFrame(
		{
			"company_id": ["A", "B"],
			"company_name": ["A", "B"],
			"peer_group_name": ["Group", "Group"],
			"broad_sector": ["X", "X"],
			"is_benchmark": [0, 0],
			"return_on_equity_pct": [10, 20],
			"return_on_capital_employed_pct": [10, 20],
			"operating_profit_margin_pct": [10, 20],
			"debt_to_equity": [2.0, 1.0],
			"interest_coverage": [10, 20],
			"asset_turnover": [1.0, 2.0],
			"free_cash_flow_cr": [10, 20],
			"revenue_cagr_5yr": [10, 20],
			"pat_cagr_5yr": [10, 20],
			"dividend_yield_pct": [1.0, 2.0],
		}
	)
	result = compute_peer_percentiles(frame)
	assert result.loc[result["company_id"] == "B", "debt_to_equity_percentile"].iloc[0] > result.loc[result["company_id"] == "A", "debt_to_equity_percentile"].iloc[0]
