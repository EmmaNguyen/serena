# Tests for Serena

This directory contains all tests for the Serena wellness companion application.

## Test Files

### `test_api.py` — 39 Python unit tests
Business logic tests for `serena_agents.py` covering:
- Chat function calls and parameter handling
- MemoryAgent context, mood logging, and journal storage
- MindfulnessAgent breathing guides
- JournalingAgent prompt generation and insights parsing
- HabitCoachAgent check-ins, streak tracking, and best-streak logic
- OrchestratorAgent intent classification and routing
- Azure service stubs (AI Search, Blob Storage, Language Pipeline)

### `test_security.py` — 46 Python security tests
Security and robustness tests for `serena_agents.py` covering:
- JSON injection in `parse_insights()`
- Memory injection via dot-notation keys
- Input sanitization (extreme values, null bytes, long strings, path traversal)
- API key handling and budget enforcement
- Orchestrator security (malicious JSON, history bounding)
- Azure service integration security
- Input type safety (non-numeric scores, empty/dot keys)
- Prompt injection attempts
- Risk flag handling
- Blob journal edge cases

### `test_api_handler.js` — 16 Node.js tests
Tests for `api/chat/index.js` (Azure Functions v3 handler) covering:
- Input validation (missing/null/wrong-type messages, null body)
- Missing environment variable handling (503 responses)
- `maxTokens` clamping (floor 1, ceiling 2000, default 300, non-numeric)
- Message history truncation (30 → last 20, exactly 20 unchanged)
- API key not leaked in response body
- API key sent in request header, not body

### `test_js_security.html` — 10 browser tests
Browser-based security tests for the HTML demos covering:
- XSS via `innerHTML`
- `localStorage` API key storage risks
- Input sanitization
- Content Security Policy (CSP) checks
- Event handler injection
- `localStorage` quota (DoS prevention)

## Running the Tests

### Python tests
```bash
# All Python tests (85 total)
python -m pytest tests/ -v

# Security tests only (46 tests)
python -m pytest tests/test_security.py -v

# API/unit tests only (39 tests)
python -m pytest tests/test_api.py -v

# With coverage
python -m pytest tests/ --cov=serena_agents --cov-report=html
```

### Node.js API handler tests
```bash
# Requires Node >= 18
node --test tests/test_api_handler.js
```

### JavaScript browser tests
Open `tests/test_js_security.html` in a browser — tests run automatically on load.

## Test Count Summary

| File | Type | Tests |
|------|------|-------|
| `test_api.py` | Python unit | 39 |
| `test_security.py` | Python security | 46 |
| `test_api_handler.js` | Node.js | 16 |
| `test_js_security.html` | Browser JS | 10 |
| **Total** | | **111** |
