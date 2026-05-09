# Contributing Guidelines

Thank you for your interest in contributing to the AI-Powered Observability Platform! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and considerate
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting remarks
- Publishing others' private information
- Any conduct that could be considered inappropriate

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- kubectl and helm
- Git

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/AI-Powered-Observability.git
cd AI-Powered-Observability

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/AI-Powered-Observability.git
```

### Set Up Development Environment

```bash
# Install Python dependencies
cd src/agents
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Node.js dependencies
cd ../frontend
npm install

cd ../chat-ui
npm install
```

### Environment Variables

```bash
# Copy example environment files
cp .env.example .env

# Edit .env with your credentials
# - OPENAI_API_KEY or GROQ_API_KEY
# - SLACK_BOT_TOKEN
# - DATABASE_URL
```

---

## Development Workflow

### Branch Naming

Use descriptive branch names following this pattern:

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/updates

Examples:
```bash
git checkout -b feature/add-memory-monitoring
git checkout -b fix/slack-notification-timeout
git checkout -b docs/update-api-reference
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/updates
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(observability): add memory leak detection"
git commit -m "fix(slack): handle timeout in approval workflow"
git commit -m "docs(api): update supervisor agent endpoints"
```

### Keep Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream main into your branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## Coding Standards

### Python Code Style

Follow [PEP 8](https://pep8.org/) and use type hints:

```python
from typing import List, Dict, Optional

def process_metrics(
    metrics: List[Dict[str, float]],
    threshold: float = 0.8,
    namespace: Optional[str] = None
) -> Dict[str, any]:
    """Process metrics and return analysis results.
    
    Args:
        metrics: List of metric dictionaries
        threshold: Alert threshold (default: 0.8)
        namespace: Kubernetes namespace filter
        
    Returns:
        Dictionary containing analysis results
    """
    # Implementation
    pass
```

### Formatting and Linting

```bash
# Format code with black
black src/agents/

# Sort imports with isort
isort src/agents/

# Lint with ruff
ruff check src/agents/

# Type check with mypy
mypy src/agents/
```

### TypeScript/JavaScript Code Style

Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript):

```typescript
interface MetricData {
  timestamp: number;
  value: number;
  labels: Record<string, string>;
}

async function fetchMetrics(
  query: string,
  timeRange: string = '5m'
): Promise<MetricData[]> {
  // Implementation
}
```

### Formatting and Linting

```bash
# Format with Prettier
npm run format

# Lint with ESLint
npm run lint

# Type check
npm run type-check
```

---

## Testing Requirements

### Python Tests

Use pytest for Python tests:

```python
# tests/test_approval_workflow.py
import pytest
from agents.common.approval_workflow import ApprovalWorkflow

@pytest.mark.asyncio
async def test_approval_timeout():
    """Test that approval times out after 5 minutes"""
    workflow = ApprovalWorkflow(timeout=5)
    
    # Mock Slack response (no approval)
    result = await workflow.request_approval(issue_details)
    
    assert result == "DENIED"
    assert workflow.reason == "timeout"

@pytest.mark.asyncio
async def test_approval_granted():
    """Test successful approval flow"""
    workflow = ApprovalWorkflow()
    
    # Mock Slack approval
    with mock_slack_approval("APPROVED"):
        result = await workflow.request_approval(issue_details)
    
    assert result == "APPROVED"
```

Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov-report=html

# Run specific test file
pytest tests/test_approval_workflow.py

# Run specific test
pytest tests/test_approval_workflow.py::test_approval_timeout
```

### JavaScript/TypeScript Tests

Use Jest for frontend tests:

```typescript
// __tests__/ChatInterface.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import ChatInterface from '../components/ChatInterface';

describe('ChatInterface', () => {
  it('sends message when submit button clicked', async () => {
    const mockSendMessage = jest.fn();
    render(<ChatInterface onSendMessage={mockSendMessage} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const button = screen.getByText('Send');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(button);
    
    expect(mockSendMessage).toHaveBeenCalledWith('Test message');
  });
});
```

Run tests:
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Integration Tests

Test agent interactions:

```python
# tests/integration/test_supervisor_routing.py
@pytest.mark.integration
async def test_supervisor_routes_to_observability_agent():
    """Test that supervisor correctly routes observability queries"""
    supervisor = SupervisorAgent()
    
    response = await supervisor.process_query(
        "Show me CPU usage for backend pods"
    )
    
    assert response["routed_to"] == "observability-agent"
    assert "promql" in response["response"]
```

### Test Coverage Requirements

- Minimum 80% code coverage for new code
- All critical paths must be tested
- Include both positive and negative test cases
- Test error handling and edge cases

---

## Pull Request Process

### Before Submitting

1. **Update from main:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests:**
   ```bash
   pytest
   npm test
   ```

3. **Run linters:**
   ```bash
   black src/agents/
   ruff check src/agents/
   npm run lint
   ```

4. **Update documentation:**
   - Update README if adding features
   - Update API_REFERENCE.md for API changes
   - Add/update docstrings

### Creating Pull Request

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature
   ```

2. **Create PR on GitHub:**
   - Use descriptive title
   - Fill out PR template
   - Link related issues
   - Add screenshots for UI changes

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Tests pass locally
   - [ ] No new warnings
   
   ## Related Issues
   Closes #123
   ```

### Review Process

1. **Automated Checks:**
   - CI/CD pipeline runs tests
   - Linters check code style
   - Coverage report generated

2. **Code Review:**
   - At least one approval required
   - Address reviewer comments
   - Keep discussions constructive

3. **Merge:**
   - Squash commits if needed
   - Update commit message
   - Delete branch after merge

---

## Documentation

### Code Documentation

**Python Docstrings:**
```python
def detect_issues(
    time_range: str = "5m",
    severity_threshold: str = "medium"
) -> List[Dict[str, any]]:
    """Detect observability issues in the specified time range.
    
    Analyzes metrics and logs to identify potential issues such as
    high CPU usage, memory leaks, or error rate spikes.
    
    Args:
        time_range: Time range to analyze (e.g., "5m", "1h", "24h")
        severity_threshold: Minimum severity to report ("low", "medium", "high")
        
    Returns:
        List of detected issues with details and recommendations
        
    Raises:
        ValueError: If time_range format is invalid
        ConnectionError: If Prometheus/Loki is unreachable
        
    Example:
        >>> issues = detect_issues(time_range="1h", severity_threshold="high")
        >>> for issue in issues:
        ...     print(f"{issue['severity']}: {issue['summary']}")
    """
    pass
```

**TypeScript JSDoc:**
```typescript
/**
 * Fetch metrics from Prometheus
 * 
 * @param query - PromQL query string
 * @param timeRange - Time range (e.g., "5m", "1h")
 * @returns Promise resolving to metric data
 * @throws {Error} If query is invalid or Prometheus is unreachable
 * 
 * @example
 * ```typescript
 * const metrics = await fetchMetrics(
 *   'rate(http_requests_total[5m])',
 *   '1h'
 * );
 * ```
 */
async function fetchMetrics(
  query: string,
  timeRange: string = '5m'
): Promise<MetricData[]> {
  // Implementation
}
```

### Architecture Documentation

Update `docs/architecture.md` for:
- New components or services
- Changes to data flow
- New integrations
- Security considerations

### API Documentation

Update `docs/API_REFERENCE.md` for:
- New endpoints
- Changed request/response formats
- New error codes
- Authentication changes

---

## Project-Specific Guidelines

### Namespace Isolation

**CRITICAL:** All Kubernetes operations MUST be scoped to `nilabja-haldar-dev`:

```python
# CORRECT
@enforce_namespace
def restart_pod(pod_name: str, namespace: str = "nilabja-haldar-dev"):
    # Implementation

# INCORRECT - Never allow cross-namespace operations
def restart_pod(pod_name: str, namespace: str):
    # This violates namespace isolation
```

### Human-in-the-Loop Approval

**CRITICAL:** All corrective actions MUST require approval:

```python
# CORRECT
@require_approval
async def restart_pod(pod_name: str):
    """Restart pod after human approval"""
    # Implementation

# INCORRECT - Never execute mutations without approval
async def restart_pod(pod_name: str):
    # This bypasses approval workflow
```

### Slack Notifications

Use Block Kit for rich formatting:

```python
# CORRECT
blocks = [
    SectionBlock(text=f"🚨 Issue: {summary}"),
    ActionsBlock(elements=[
        ButtonElement(text="✅ Approve", action_id="approve"),
        ButtonElement(text="❌ Deny", action_id="deny")
    ])
]

# INCORRECT - Plain text is less informative
message = f"Issue: {summary}. Approve? (yes/no)"
```

---

## Questions or Issues?

- **Slack:** #observability-dev channel
- **GitHub Issues:** For bug reports and feature requests
- **Email:** maintainers@example.com

---

**Thank you for contributing!** 🎉

**Made with Bob** 🤖