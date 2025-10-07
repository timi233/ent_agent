# Makefile for City Brain System

# Python interpreter
PYTHON = python3
PIP = pip

# Default target
.PHONY: help install test run clean

help:
	@echo "City Brain System - Makefile"
	@echo "============================"
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make run         - Start the server"
	@echo "  make clean       - Clean cache files"
	@echo "  make docker      - Build and run with Docker"
	@echo "  make docker-down - Stop Docker containers"

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest tests/ -v

test-imports:
	$(PYTHON) test_imports.py

run:
	$(PYTHON) start.sh

clean:
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -f .coverage

docker:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f