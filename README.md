# 🌿 Serena

**AI-Powered Mindfulness, Journaling & Habit-Tracking Assistant**

> A multi-agent AI system that meets you where you are — not where productivity culture says you should be.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Azure%20Static%20Web%20Apps-0078D4?style=for-the-badge&logo=microsoftazure)](https://your-app.azurestaticapps.net)
[![Built with Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![Hackathon](https://img.shields.io/badge/Hackathon-2026-F59E0B?style=for-the-badge)]()

---

## The Problem

Mental wellness apps are broken in three ways:

- **They start cold.** Every session, you re-explain yourself.
- **They punish you.** Missed your streak? Red X. Guilt trip. Churn.
- **They're generic.** The same breathing script for everyone, regardless of what you actually need right now.

73% of people who download wellness apps abandon them within a week. The apps don't know them — so why would they stay?

---

## What Serena Does Differently

Serena is a **context-first, multi-agent AI system** built on Azure. Instead of one AI trying to do everything, five specialized agents collaborate — each with a focused role, all sharing a persistent memory of who you are.

| Agent | Role |
|---|---|
| **Orchestrator** | Classifies intent, routes to the right agent, assembles context |
| **Memory Agent** | Maintains tiered context across sessions (Redis → Cosmos DB → AI Search) |
| **Mindfulness Coach** | Guided breathing, grounding, personalized to your history |
| **Journaling Agent** | Context-aware prompts and empathetic reflection |
| **Habit Coach** | Zero-guilt check-ins, streak recovery, motivational insights |
| **Insights Pipeline** | Async correlation of mood, habits, and journal sentiment over time |

---

## Live Demo

🔗 **[Try the interactive demo →](https://your-app.azurestaticapps.net)**

The demo runs entirely client-side — no API keys or sign-up required. Use the sidebar buttons to walk through three scripted scenes, or type freely to explore the routing logic.

**Scene 1 — Mindfulness:** Stress detected → Memory Agent recalled "prefers box breathing" → adaptive guided session

**Scene 2 — Journaling:** Mood-aware prompt generated → empathetic AI response → async sentiment pipeline runs

**Scene 3 — Habit Tracking:** Missed streak handled with zero guilt → Insights Agent surfaces a mood-habit correlation

---

## Architecture

```
User Message (HTML Demo)
     │
     ▼
┌─────────────────────────────┐
│  Orchestrator Agent (Python)│  ← Azure OpenAI (GPT-4o-mini)
│   - Intent classification   │
│   - Context assembly        │
│   - Agent routing           │
└──────────┬──────────────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐  ┌──────────────────────────────┐
│ Memory  │  │   Specialized Agents          │
│  Agent  │  │  ┌─────────────────────────┐ │
│ (in-mem │  │  │  Mindfulness Coach Agent │ │
│  stub)  │  │  ├─────────────────────────┤ │
│         │  │  │  Journaling Agent        │ │
│ Tiered: │  │  ├─────────────────────────┤ │
│ Redis   │  │  │  Habit Coach Agent       │ │
│ Cosmos  │  │  ├─────────────────────────┤ │
│ Search  │  │  │  Insights Pipeline       │ │
└─────────┘  └──────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Azure OpenAI (GPT-4o) │
              │  Primary responses     │
              └───────────────────────┘
```

---

## Azure Stack

| Service | Purpose | Status |
|---|---|---|
| Azure OpenAI (GPT-4o) | Primary agent responses | **Required** |
| Azure OpenAI (GPT-4o-mini) | Intent classification & routing | **Required** |
| Azure AI Language | Sentiment analysis (optional, falls back to GPT-4o-mini) | Optional |
| Azure AI Search | Long-term semantic memory | Planned |
| Azure Cosmos DB | Structured user data, habit logs | Planned |
| Azure Blob Storage | Encrypted journal content | Planned |
| Azure Cache for Redis | Hot session context | Planned |
| Azure Service Bus | Async sentiment pipeline | Planned |
| Azure Static Web Apps | Frontend hosting | Optional |

---

## Run Locally

### Option 1: HTML Demo (No API keys required)

Open `index.html` or `demo.html` in a browser. These run in mock mode with pre-scripted responses — no Azure credentials needed.

### Option 2: Python Backend with Azure OpenAI

```bash
# 1. Install dependencies
pip install openai

# 2. Set environment variables
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
export AZURE_OPENAI_API_KEY=your-key-here
export AZURE_OPENAI_API_VERSION=2024-12-01-preview
export AZURE_GPT4O_DEPLOYMENT=gpt-4o
export AZURE_GPT4O_MINI_DEPLOYMENT=gpt-4o-mini

# Optional: Azure AI Language (falls back to GPT-4o-mini if unset)
export AZURE_AI_LANGUAGE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
export AZURE_AI_LANGUAGE_KEY=your-key-here

# 3. Run the scripted demo
python serena_agents.py

# 4. Or free-form interactive mode
python serena_agents.py interactive
```

> **Note:** Storage services (Cosmos DB, Blob, Redis, AI Search) run as in-memory stubs in the current implementation. Only Azure OpenAI is required for full functionality.

---

## Deploy to Azure (Optional)

The static HTML demos can be deployed to Azure Static Web Apps at no cost.

### Prerequisites
- Azure subscription (free trial works)
- GitHub account

### Steps

1. Fork this repo
2. Go to [portal.azure.com](https://portal.azure.com) → **Create a resource → Static Web App**
3. Connect your forked repo, set **App location** to `/`, leave Api and Output locations blank
4. Click **Create** — Azure auto-generates a GitHub Actions deploy workflow
5. Your app is live at `https://<generated-name>.azurestaticapps.net` within ~2 minutes

**Estimated cost: $0/month** (Free plan, no time limit)

---

## Design Principles

**1. Context-first, not session-first**
Every agent queries Memory before responding. Serena knows you across sessions.

**2. Zero guilt mechanics**
No red streaks. No penalty scores. Missed days are "attempted" — the system meets you where you are.

**3. Separation of concerns**
The Mindfulness Coach doesn't know habit streak logic. The Habit Coach doesn't give breathing advice. Clean agents, clean prompts, easier iteration.

**4. Privacy as a feature**
Journal content is encrypted at rest with user-specific keys. No ads. No data selling. One-tap full delete.

---

## Testing

111 tests covering agent logic, API surface, security hardening, and the Azure Functions handler.

```bash
# All Python tests (85 total)
python -m pytest tests/ -v

# Security tests only (46 tests)
python -m pytest tests/test_security.py -v

# API/unit tests only (39 tests)
python -m pytest tests/test_api.py -v

# With coverage
python -m pytest tests/ --cov=serena_agents --cov-report=html

# Node.js API handler tests (16 tests, requires Node >= 18)
node --test tests/test_api_handler.js
```

JavaScript security tests (10 tests): open `tests/test_js_security.html` in a browser — they run automatically on load.

See [`tests/TEST_SUMMARY.md`](tests/TEST_SUMMARY.md) for the full test inventory.

---

## Files in this Repo

```
├── index.html               # Landing page
├── demo.html                # Live demo with mock/live API toggle
├── api-demo.html            # API demo with manual key entry
├── staticwebapp.config.json # Azure Static Web Apps routing config
├── serena_agents.py         # Python multi-agent backend (Azure OpenAI)
├── api/
│   └── chat/index.js        # Azure Functions chat proxy (Node.js)
└── tests/
    ├── test_api.py          # 39 unit/API tests
    ├── test_security.py     # 46 security tests
    ├── test_api_handler.js  # 16 Node.js tests for Azure Functions handler
    ├── test_js_security.html # 10 browser-based JS security tests
    ├── TEST_SUMMARY.md      # Full test inventory
    └── README.md            # Test documentation
```

---

## Team

Built for the 2026 Hackathon.

---

*"Three agents. One coherent experience. Alex came in overwhelmed — and in three minutes, they breathed, they reflected, and they got a reason to try again tomorrow."*

🌿
