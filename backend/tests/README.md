# StockBro Backend Tests

This directory contains all test files for the StockBro backend.

## Structure

- `unit/` - Unit tests for individual functions and classes
- `integration/` - Integration tests for API endpoints and services  
- `e2e/` - End-to-end tests for complete user flows

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=app --cov-report=html
```

## Current Tests

- `integration/test_complete_integration.py` - Full agent integration test
- `integration/test_groq_integration.py` - Groq LLM integration test
