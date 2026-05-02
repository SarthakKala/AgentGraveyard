#!/usr/bin/env bash
set -e

# Prefer python3; fall back to `python` (some environments only have python)
if command -v python3 &>/dev/null; then
  PY=python3
elif command -v python &>/dev/null; then
  PY=python
else
  echo "Python not found. Install Python 3.10+ and try again."
  exit 1
fi

echo ""
echo "🪦  Agent Graveyard — Setup"
echo "================================"

# ── Check Python version ──────────────────────────────────────────
python_version=$($PY --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# ── Create virtual environment if not exists ──────────────────────
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  $PY -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo "✓ Virtual environment active"

# ── Install backend dependencies ──────────────────────────────────
echo ""
echo "Installing backend dependencies..."
pip install -q -r backend/requirements.txt
echo "✓ Backend dependencies installed"

# ── Install SDK in editable mode ──────────────────────────────────
echo "Installing SDK..."
pip install -q -e ./sdk
echo "✓ SDK installed (graveyard CLI available)"

# ── Install demo dependencies ─────────────────────────────────────
pip install -q requests beautifulsoup4
echo "✓ Demo dependencies installed"

# ── Check .env exists ─────────────────────────────────────────────
if [ ! -f "backend/.env" ]; then
  echo ""
  echo "⚠️  backend/.env not found."
  echo "   Run: cp backend/.env.example backend/.env"
  echo "   Then fill in your API keys and run this script again."
  exit 1
fi
echo "✓ backend/.env found"

# ── Run environment check ─────────────────────────────────────────
echo ""
echo "Checking environment..."
if ! $PY scripts/check_env.py; then
  echo ""
  echo "❌ Fix the issues above before continuing."
  exit 1
fi

# ── Seed the database ─────────────────────────────────────────────
echo ""
echo "Seeding community failure database..."
echo "(First run downloads embedding model ~400MB — please wait)"
(cd backend && $PY ../seed_data/seed.py)
echo "✓ Database seeded"

# ── Start the backend ─────────────────────────────────────────────
echo ""
echo "================================"
echo "✅  Setup complete!"
echo ""
echo "Starting backend on http://localhost:8000 ..."
echo "Press Ctrl+C to stop."
echo ""
echo "In a NEW terminal tab, run:"
echo "  source .venv/bin/activate"
echo "  python demo/demo_agent.py"
echo "================================"
echo ""

cd backend && exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
