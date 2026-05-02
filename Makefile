# Agent Graveyard — common tasks (Unix/Git Bash/WSL). On Windows PowerShell, run the commands manually.

.PHONY: help venv install-sdk install-backend seed backend verify

help:
	@echo "Targets:"
	@echo "  make install-backend  pip install backend requirements into active venv"
	@echo "  make install-sdk      pip install SDK in editable mode (graveyard CLI)"
	@echo "  make seed             python seed_data/seed.py --force"
	@echo "  make backend          run FastAPI on :8000"
	@echo "  make verify           smoke-check backend health + optional overview"

venv:
	python -m venv .venv
	@echo "Activate: source .venv/bin/activate  (Windows: .venv\\Scripts\\Activate.ps1)"

install-backend:
	python -m pip install -r backend/requirements.txt

install-sdk:
	python -m pip install -e ./sdk

seed:
	python seed_data/seed.py --force

backend:
	cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

verify:
	python scripts/verify_setup.py
