# Nifty 100 Financial Intelligence Platform

Production-grade financial analytics platform for all 92 Nifty 100 companies with comprehensive dashboard, screener, and valuation modules.

## What is included

- A clean `src/` package layout for ETL, analytics, dashboard, and API work
- Complete ETL pipeline with data normalization, loading, and validation
- Financial ratios calculation engine with 20+ metrics
- Stock screener with 6 presets and custom filters
- Peer comparison with 11 industry groups
- Capital allocation pattern analysis
- Valuation module with FCF yield and sector P/E analysis
- **8-screen Streamlit dashboard** with interactive visualizations
- Project-local pytest configuration and comprehensive unit tests

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Setup directories
make setup
```

### 2. Load Data

```bash
# Run ETL pipeline
make load

# Validate data quality
make validate
```

### 3. Run Dashboard

```bash
# Launch Streamlit dashboard on http://localhost:8501
make dashboard

# Or directly:
streamlit run src/dashboard/app.py
```

### 4. Generate Valuation Reports

```bash
# Generate valuation analysis
python -m src.analytics.valuation

# Outputs:
# - output/valuation_summary.xlsx (all 92 companies)
# - output/valuation_flags.csv (Caution/Discount companies)
```

## Dashboard Screens

The Streamlit dashboard includes 8 comprehensive screens:

### 1. 🏠 Home / Market Overview
- 6 KPI tiles: Avg ROE, Median P/E, Median D/E, Total Companies, Median Rev CAGR 5yr, Debt-Free count
- Sector distribution donut chart (11 sectors)
- Top 5 companies by composite quality score
- Year selector (2019-2024) with dynamic metric updates
- Sector median ROE bar chart

### 2. 🏢 Company Profile
- Autocomplete search for all 92 companies
- Company card with sector, sub-sector, and description
- 6 KPI tiles: ROE, ROCE, NPM, D/E, Rev CAGR 5yr, FCF with YoY deltas
- 10-year Revenue & Net Profit bar chart
- ROE/ROCE dual-axis trend line
- Pros/Cons badges

### 3. 🔎 Stock Screener
- 10 metric sliders: ROE, ROCE, NPM, Current Ratio, D/E, Interest Coverage, Rev CAGR, FCF, P/E, Market Cap
- 6 preset filters: Quality Leaders, Value Buys, Growth Stars, Dividend Kings, Debt-Free, High ROE
- Live-updating results table
- CSV export functionality
- Result count display

### 4. 🔄 Peer Comparison
- 11 peer group dropdown
- Interactive radar chart (company vs peer average)
- 6-metric comparison: ROE, ROCE, NPM, Current Ratio, D/E, Interest Coverage
- Benchmark company highlighting
- Detailed KPI comparison table

### 5. 📈 Trends Analysis
- Company search
- Multi-metric selector (up to 3 metrics)
- 10-year trend line chart
- Year-over-year change annotations
- YoY comparison table

### 6. 🏢 Sector Analysis
- Sector selector
- Bubble chart: Revenue vs ROE (sized by Market Cap, colored by sub-sector)
- Sector median KPI comparison
- Company listing by sector

### 7. 💰 Capital Allocation
- Interactive treemap by 8 allocation patterns
- Pattern distribution statistics
- Company grouping by allocation strategy
- Pattern descriptions and definitions

### 8. 📄 Annual Reports
- Company search
- BSE PDF download links
- Report availability status
- Year-by-year report listing

## Data Architecture

```
data/
├── nifty100.db              # SQLite database
├── raw/                     # Source Excel files
│   ├── companies.xlsx
│   ├── profitandloss.xlsx
│   ├── balancesheet.xlsx
│   ├── cashflow.xlsx
│   ├── analysis.xlsx
│   ├── prosandcons.xlsx
│   └── documents.xlsx
└── supporting/              # Supporting data
    ├── financial_ratios.xlsx
    ├── market_cap.xlsx
    ├── peer_groups.xlsx
    ├── sectors.xlsx
    └── stock_prices.xlsx

output/
├── screener_output.xlsx
├── peer_comparison.xlsx
├── capital_allocation.csv
├── valuation_summary.xlsx
└── valuation_flags.csv
```

## Testing

```bash
# Run all tests
make test

# Run Sprint 1 tests
make test-sprint1

# Run specific test suite
pytest tests/screener/ -v
```

## Project Structure

```
src/
├── etl/                     # Data pipeline
│   ├── loader.py
│   ├── normaliser.py
│   └── validator.py
├── analytics/               # Analytics modules
│   ├── ratios.py
│   ├── valuation.py
│   └── capital_allocation.py
├── screener/                # Stock screener
│   └── engine.py
├── kpi/                     # KPI calculations
│   ├── quality_score.py
│   └── peer_analysis.py
├── dashboard/               # Streamlit dashboard
│   ├── app.py
│   ├── utils/
│   │   └── db.py           # Cached data access layer
│   └── pages/              # 8 dashboard screens
│       ├── 01_home.py
│       ├── 02_profile.py
│       ├── 03_screener.py
│       ├── 04_peers.py
│       ├── 05_trends.py
│       ├── 06_sectors.py
│       ├── 07_capital.py
│       └── 08_reports.py
└── api/                     # FastAPI endpoints
    └── main.py
```

## Technology Stack

- **Backend**: Python 3.11+
- **Database**: SQLite3
- **Data Processing**: pandas, numpy, scipy
- **Visualization**: Plotly, matplotlib
- **Dashboard**: Streamlit
- **API**: FastAPI, uvicorn
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, ruff

## Environment Requirements

- Python 3.11 or higher
- 8GB RAM (recommended)
- 500MB disk space
- Modern web browser for dashboard

## Performance Features

- **Data Caching**: All dashboard queries cached for 10 minutes
- **Query Optimization**: Indexed database queries
- **Lazy Loading**: Data loaded only when screens are accessed
- **Connection Management**: Efficient SQLite connection pooling

## Sprint Completion Status

- ✅ Sprint 1: Data Foundation
- ✅ Sprint 2: Ratio Engine  
- ✅ Sprint 3: Screener & Peer Engine
- ✅ Sprint 4: Dashboard & Valuation Module

## Troubleshooting

### Dashboard won't start
```bash
# Check if streamlit is installed
pip show streamlit

# Reinstall if needed
pip install streamlit>=1.30.0
```

### Data not loading
```bash
# Verify database exists
ls data/nifty100.db

# Reload data
make load
```

### Cache issues
```bash
# Clear Streamlit cache
streamlit cache clear
```

## License

This project is for educational purposes.

