.PHONY: setup load validate test test-sprint1 clean report dashboard api

setup:
	mkdir -p output reports/tearsheets reports/sector reports/portfolio reports/radar_charts
	cp config/.env.template .env 2>/dev/null || true
	@echo "Directives created."

load:
	python -m src.etl.loader

validate:
	python -m src.etl.validator

test:
	pytest tests/ --html=output/pytest_report.html --cov=src --cov-report=html -v --tb=short

test-sprint1:
	pytest tests/etl tests/dq -v --tb=short

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --port 8000 --reload

report:
	python -m src.reports.portfolio_report

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true; \
	find . -name "*.pyc" -delete 2>/dev/null || true; \
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true; \
	echo "Cleaned."
