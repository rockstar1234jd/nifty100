PYTHONPATH := $(CURDIR)/src/etl:$(CURDIR)/src/analytics:$(CURDIR)/src

.PHONY: load ratios test report dashboard api clean validate setup

setup:
	mkdir -p output reports/tearsheets reports/sector reports/portfolio reports/radar_charts
	cp config/.env.template .env 2>/dev/null || true
	@echo "✅ Directories and .env created."

load:
	python src/etl/loader.py

validate:
	python src/etl/validator.py

test-sprint1:
	pytest tests/etl tests/dq -v --tb=short
