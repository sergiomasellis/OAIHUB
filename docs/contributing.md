# Contributing Guide

Thank you for your interest in contributing to the AI Agent Tracking Dashboard! This guide will help you get started with development and contribution processes.

## 🤝 How to Contribute

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/ai-agent-tracking-dashboard.git
cd ai-agent-tracking-dashboard

# Add upstream remote
git remote add upstream https://github.com/original-owner/ai-agent-tracking-dashboard.git
```

### 2. Set Up Development Environment
```bash
# Quick setup with Docker
docker-compose up --build

# Or manual setup
# Follow the Setup Guide in docs/setup-guide.md
```

### 3. Create a Feature Branch
```bash
# Create a descriptive branch name
git checkout -b feature/add-new-chart-type

# Or for bug fixes
git checkout -b fix/dashboard-loading-issue

# Or for documentation
git checkout -b docs/update-api-reference
```

### 4. Make Your Changes
- Follow the coding standards outlined below
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 5. Commit Your Changes
```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new performance metrics chart

- Add response time distribution chart
- Update dashboard layout to accommodate new chart
- Add unit tests for chart component
- Update API to support new metrics data"

# Push to your fork
git push origin feature/add-new-chart-type
```

### 6. Create a Pull Request
1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the pull request template
5. Wait for review and address any feedback

## 📋 Contribution Types

### 🐛 Bug Reports
- Use the GitHub issue tracker
- Include detailed reproduction steps
- Provide system information and error logs
- Include screenshots for UI issues

### ✨ Feature Requests
- Clearly describe the feature and its benefits
- Provide use cases and examples
- Consider backward compatibility

### 📝 Documentation
- Fix typos and improve clarity
- Add missing documentation
- Translate documentation to other languages
- Create tutorials and guides

### 🧪 Testing
- Write unit tests for new features
- Improve existing test coverage
- Add integration tests
- Test edge cases and error conditions

### 🎨 UI/UX Improvements
- Improve dashboard design and usability
- Enhance accessibility
- Optimize performance
- Add new chart types or visualizations

## 📖 Code of Conduct

### Our Standards
- **Be respectful** and inclusive
- **Use welcoming language**
- **Be collaborative**
- **Focus on constructive feedback**
- **Show empathy** towards other contributors

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Any other unethical or unprofessional behavior

## 🏗️ Development Setup

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for manual frontend setup)
- Python 3.8+ (for manual backend setup)

### Environment Variables
```bash
# Backend (.env)
AWS_REGION=us-east-1
DYNAMODB_TABLE_EVENTS=ai-agent-events-dev
DYNAMODB_TABLE_METRICS=ai-agent-metrics-dev

# Frontend (.env)
REACT_APP_API_URL=http://localhost:8001/api/v1
```

### Running Tests
```bash
# Backend tests
cd backend
source venv/bin/activate
pytest

# Frontend tests
cd frontend
npm test

# End-to-end tests (if available)
npm run test:e2e
```

## 📋 Coding Standards

### Python (Backend)

#### Code Style
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 88 characters (Black formatter default)
- Use descriptive variable and function names

#### Example
```python
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class AgentMetricsService:
    """Service for handling agent metrics operations."""

    def get_agent_metrics(
        self,
        agent_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AgentMetrics]:
        """Retrieve metrics for a specific agent within date range."""
        # Implementation here
        pass
```

#### Imports
```python
# Standard library imports
import json
from datetime import datetime
from typing import Optional, List

# Third-party imports
from fastapi import FastAPI, HTTPException
import boto3
from pydantic import BaseModel

# Local imports
from .models import AgentEvent
from .config import Config
```

### TypeScript/React (Frontend)

#### Code Style
- Use TypeScript for all new code
- Follow ESLint and Prettier configurations
- Use functional components with hooks
- Maximum line length: 100 characters

#### Example
```typescript
import React, { useState, useEffect } from 'react';
import { AgentMetrics } from '../types';

interface MetricsCardProps {
  metrics: AgentMetrics;
  loading?: boolean;
  error?: string;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  metrics,
  loading = false,
  error
}) => {
  if (loading) {
    return <Card><Text>Loading metrics...</Text></Card>;
  }

  if (error) {
    return <Card><Text color="error">{error}</Text></Card>;
  }

  return (
    <Card>
      <Heading level={3}>Agent Metrics</Heading>
      <Text>Total Messages: {metrics.total_messages}</Text>
      <Text>Success Rate: {calculateSuccessRate(metrics)}%</Text>
    </Card>
  );
};
```

#### Component Structure
```typescript
// components/
├── common/           # Shared components
├── dashboard/        # Dashboard-specific components
├── charts/          # Chart components
└── forms/           # Form components

// types/
└── index.ts         # TypeScript type definitions

// services/
└── apiService.ts    # API communication layer
```

## 🧪 Testing Guidelines

### Unit Tests
```python
# backend/test_agent_service.py
import pytest
from datetime import datetime
from app.services.agent_service import AgentService

class TestAgentService:
    @pytest.fixture
    def agent_service(self):
        return AgentService()

    def test_get_agent_metrics_success(self, agent_service):
        """Test successful retrieval of agent metrics."""
        metrics = agent_service.get_agent_metrics("test-agent")

        assert metrics is not None
        assert metrics.agent_id == "test-agent"
        assert metrics.total_messages >= 0

    def test_get_agent_metrics_not_found(self, agent_service):
        """Test handling of non-existent agent."""
        with pytest.raises(HTTPException) as exc_info:
            agent_service.get_agent_metrics("non-existent-agent")

        assert exc_info.value.status_code == 404
```

```typescript
// frontend/src/components/MetricsCard.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MetricsCard } from './MetricsCard';
import { AgentMetrics } from '../types';

const mockMetrics: AgentMetrics = {
  agent_id: 'test-agent',
  date: '2024-01-07',
  total_messages: 100,
  total_responses: 95,
  total_errors: 5,
  average_response_time: 850,
  total_tokens_used: 5000,
  average_feedback_score: 4.2,
  unique_users: 25
};

describe('MetricsCard', () => {
  it('renders metrics correctly', () => {
    render(<MetricsCard metrics={mockMetrics} />);

    expect(screen.getByText('Total Messages: 100')).toBeInTheDocument();
    expect(screen.getByText('Success Rate: 95%')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<MetricsCard metrics={mockMetrics} loading={true} />);

    expect(screen.getByText('Loading metrics...')).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<MetricsCard metrics={mockMetrics} error="Failed to load" />);

    expect(screen.getByText('Failed to load')).toBeInTheDocument();
  });
});
```

### Integration Tests
```python
# backend/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_record_and_retrieve_event(client):
    """Test full flow of recording and retrieving an event."""
    # Record an event
    event_data = {
        "agent_id": "test-agent",
        "timestamp": "2024-01-07T10:00:00Z",
        "message_type": "user_message",
        "content": "Hello, world!"
    }

    response = client.post("/api/v1/agents/test-agent/events", json=event_data)
    assert response.status_code == 200

    # Retrieve metrics
    response = client.get("/api/v1/agents/test-agent/metrics?days=1")
    assert response.status_code == 200

    data = response.json()
    assert data["agent_id"] == "test-agent"
    assert data["metrics"]["total_messages"] == 1
```

## 📝 Documentation Standards

### README Updates
- Keep README.md current with latest features
- Include code examples for new functionality
- Update setup instructions as needed

### API Documentation
- Document all new endpoints in `docs/api-reference.md`
- Include request/response examples
- Document error codes and handling

### Code Documentation
```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Brief description of what the function does.

    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2

    Returns:
        dict: Description of return value

    Raises:
        ValueError: When something goes wrong
        HTTPException: For API errors

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success', 'data': 'processed'}
    """
    pass
```

## 🔄 Pull Request Process

### PR Template
```markdown
## Description
Brief description of the changes made.

## Changes Made
- [ ] Feature: Added new dashboard chart
- [ ] Bug Fix: Fixed API timeout issue
- [ ] Documentation: Updated API reference
- [ ] Tests: Added unit tests for new feature

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] No breaking changes

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Related Issues
Closes #123
```

### Review Process
1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: At least one maintainer reviews the code
3. **Testing**: Reviewer tests the functionality
4. **Approval**: PR is approved and merged
5. **Deployment**: Changes are deployed to staging/production

## 🚀 Release Process

### Versioning
We follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist
- [ ] Update version numbers in all relevant files
- [ ] Update CHANGELOG.md with release notes
- [ ] Ensure all tests pass
- [ ] Update documentation
- [ ] Create git tag
- [ ] Deploy to production
- [ ] Announce release

## 🎯 Best Practices

### Git Workflow
```bash
# Keep your branch up to date
git fetch upstream
git rebase upstream/main

# Squash commits before PR
git rebase -i HEAD~n  # n = number of commits to squash

# Write good commit messages
# Format: type(scope): description
# Examples:
# feat(dashboard): add new metrics chart
# fix(api): resolve timeout issue
# docs(readme): update setup instructions
# test(metrics): add unit tests for calculation logic
```

### Code Quality
- **Write tests** for all new functionality
- **Follow existing patterns** in the codebase
- **Keep functions small** and focused
- **Use meaningful names** for variables and functions
- **Add type hints** in Python and TypeScript
- **Handle errors gracefully**
- **Write documentation** for complex logic

### Performance Considerations
- **Optimize database queries** - use indexes effectively
- **Cache frequently accessed data**
- **Minimize API calls** from frontend
- **Use pagination** for large datasets
- **Compress responses** where appropriate
- **Monitor memory usage** in long-running processes

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussion
- **Pull Requests**: For code contributions

### Asking for Help
When asking for help, please provide:
1. **Clear description** of the issue or question
2. **Steps to reproduce** (for bugs)
3. **Expected vs actual behavior**
4. **Environment details** (OS, versions, etc.)
5. **Code snippets** or error messages
6. **Screenshots** (for UI issues)

## 🙏 Recognition

Contributors will be recognized in:
- **Contributors list** in README.md
- **Release notes** for significant contributions
- **GitHub's contributor insights**

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the AI Agent Tracking Dashboard! Your efforts help make this tool better for the entire community. 🚀