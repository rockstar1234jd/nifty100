import pandas as pd

from src.screener.engine import apply_filter, load_screener_config, sort_screened_frame


def test_screener_config_contains_presets_and_filters() -> None:
	config = load_screener_config()
	assert len(config["screener"]["filters"]) == 15
	assert len(config["screener"]["presets"]) == 6


def test_sector_bypass_and_icr_passthrough_rules() -> None:
	frame = pd.DataFrame(
		{
			"broad_sector": ["Financials", "Industrials"],
			"debt_to_equity": [9.9, 0.5],
			"interest_coverage": [0.2, 99.0],
			"icr_label": ["Computed", "Debt Free"],
		}
	)
	max_de_rule = {"column": "debt_to_equity", "operator": "<=", "sector_bypass": ["Financials"]}
	icr_rule = {"column": "interest_coverage", "operator": ">=", "icr_passthrough": True}
	assert apply_filter(frame, max_de_rule, 1.0).tolist() == [True, True]
	assert apply_filter(frame, icr_rule, 10.0).tolist() == [False, True]


def test_sort_screened_frame_adds_sector_relative_score() -> None:
	frame = pd.DataFrame(
		{
			"company_id": ["A", "B"],
			"broad_sector": ["IT", "IT"],
			"composite_quality_score": [60.0, 80.0],
			"market_cap_crore": [10.0, 20.0],
		}
	)
	result = sort_screened_frame(frame)
	assert "sector_relative_score" in result.columns
	assert result.iloc[0]["company_id"] == "B"
