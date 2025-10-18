.PHONY: help install dev-install test lint format clean run config-check

help:
	@echo "3DAgency - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install the package"
	@echo "  make dev-install  Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"
	@echo "  make type-check   Run type checking"
	@echo ""
	@echo "Running:"
	@echo "  make run PROMPT='your prompt'  Generate a scene"
	@echo "  make config-check              Check configuration"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove build artifacts"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=agency3d --cov-report=html --cov-report=term

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	@if [ -z "$(PROMPT)" ]; then \
		echo "Usage: make run PROMPT='your scene description'"; \
		exit 1; \
	fi
	3dagency create "$(PROMPT)"

config-check:
	3dagency config-check

# Quick start for new developers
setup: dev-install
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "1. Copy .env.example to .env"
	@echo "2. Add your API key to .env"
	@echo "3. Set BLENDER_PATH in .env"
	@echo "4. Run: make config-check"
	@echo "5. Generate your first scene: make run PROMPT='a cozy cafe'"
