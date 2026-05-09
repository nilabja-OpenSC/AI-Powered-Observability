# AI Agents Setup Guide

Quick setup guide for the AI agents Python environment.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)

## Installation Steps

### 1. Create Virtual Environment

```bash
# Navigate to agents directory
cd src/agents

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

#### Production Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web framework)
- OpenAI & Groq (LLM providers)
- ChromaDB (vector store)
- Kubernetes client
- Slack SDK
- Confluence API
- Structlog (logging)
- And more...

#### Development Dependencies (Optional)

```bash
pip install -r requirements-dev.txt
```

This additionally installs:
- pytest (testing)
- black, ruff, mypy (code quality)
- ipython (enhanced shell)
- Documentation tools
- Profiling tools

### 3. Verify Installation

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify key packages
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import openai; print(f'OpenAI: {openai.__version__}')"
python -c "import structlog; print('Structlog: OK')"
```

### 4. Configure Environment Variables

```bash
# Copy environment template
cp ../../.env.example .env

# Edit .env with your credentials
# Required:
# - OPENAI_API_KEY or GROQ_API_KEY
# - SLACK_BOT_TOKEN
# - DATABASE_URL
```

### 5. Test Setup

```bash
# Run a simple test
python -c "
from agents.common.llm_client import LLMClient
print('LLM Client imported successfully')
"

# Start supervisor agent (test)
cd supervisor
python main.py
# Should start on http://localhost:8080
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'structlog'`

**Solution:**
```bash
pip install structlog
```

### Issue: `ImportError: cannot import name 'OpenAI' from 'openai'`

**Solution:**
```bash
pip install --upgrade openai
```

### Issue: `kubernetes.config.config_exception.ConfigException`

**Solution:**
```bash
# Ensure kubeconfig is set
export KUBECONFIG=~/.kube/config

# Or set in .env
echo "KUBECONFIG=/path/to/kubeconfig" >> .env
```

### Issue: ChromaDB persistence errors

**Solution:**
```bash
# Create chroma data directory
mkdir -p chroma_data

# Set permissions
chmod 755 chroma_data
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov-report=html

# Run specific test file
pytest tests/test_approval_workflow.py
```

### Code Formatting

```bash
# Format code with black
black .

# Sort imports
isort .

# Lint with ruff
ruff check .

# Type check with mypy
mypy agents/
```

### Running Individual Agents

```bash
# Supervisor Agent (port 8080)
cd supervisor
python main.py

# Observability Agent (port 8081)
cd ../observability
python main.py

# Pod Recovery Agent (port 8082)
cd ../pod-recovery
python main.py

# Backup/Restore Agent (port 8083)
cd ../backup-restore
python main.py
```

## Docker Setup (Alternative)

If you prefer Docker:

```bash
# Build image
docker build -t supervisor-agent -f Dockerfile.supervisor .

# Run container
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN \
  supervisor-agent
```

## Updating Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade openai

# Freeze current versions
pip freeze > requirements-lock.txt
```

## Troubleshooting

### Check Python Path

```bash
which python
python -c "import sys; print(sys.executable)"
```

### Check Installed Packages

```bash
pip list | grep -E "fastapi|openai|structlog|kubernetes"
```

### Clear Cache

```bash
# Clear pip cache
pip cache purge

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Reinstall from Scratch

```bash
# Deactivate and remove venv
deactivate
rm -rf venv

# Recreate and reinstall
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. Configure environment variables in `.env`
2. Set up Kubernetes access (kubeconfig)
3. Configure Slack bot token
4. Test individual agents
5. Deploy to Kubernetes with Helm charts

## Support

For issues:
- Check logs: `tail -f /var/log/agent.log`
- Review documentation: `docs/`
- Open GitHub issue with error details

---

**Made with Bob** 🤖