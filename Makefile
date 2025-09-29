# API Assignment Test Suite Makefile

.PHONY: help install validate test test-csv test-api test-security test-data test-performance test-all clean

help: ## Show this help message
	@echo "API Assignment Test Suite"
	@echo "========================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install test dependencies
	pip install -r test_requirements.txt

validate: ## Validate test environment setup
	python validate_setup.py

test-csv: ## Run CSV converter tests
	python run_tests.py csv

test-api: ## Run API endpoint tests (requires API running)
	python run_tests.py api

test-security: ## Run SQL injection security tests (requires API running)
	python run_tests.py security

test-data: ## Run data integrity tests
	python run_tests.py data

test-performance: ## Run performance tests (requires API running)
	python run_tests.py performance

test-all: ## Run all tests
	python run_tests.py all

test: test-all ## Alias for test-all

clean: ## Clean up test artifacts
	rm -f test_report.json test_report.html
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

setup: install ## Setup test environment
	@echo "Setting up test environment..."
	@if [ ! -f data.db ]; then \
		echo "Creating database..."; \
		python csv_to_sqlite.py data.db county_health_rankings.csv; \
		python csv_to_sqlite.py data.db zip_county.csv; \
	fi
	@echo "Test environment setup complete!"
	@echo "Run 'make validate' to check everything is working"

start-api: ## Start the API server
	@echo "Starting API server on localhost:5001..."
	@echo "Press Ctrl+C to stop"
	python api/index.py

check: validate ## Alias for validate
