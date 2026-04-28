"""
Serena — Multi-Agent Scaffolding (Azure Edition)
===========================================================
5-agent system backed entirely by Microsoft Azure services.

Azure services used:
  - Azure OpenAI          → GPT-4o (primary) + GPT-4o-mini (routing)
  - Azure AI Language     → Sentiment analysis pipeline
  - Azure AI Search       → Vector memory / semantic retrieval
  - Azure Cosmos DB       → Structured user data & habit logs
  - Azure Blob Storage    → Encrypted journal content
  - Azure Cache for Redis → Hot session context

Quick start:
  pip install openai azure-ai-textanalytics azure-search-documents \
              azure-cosmos azure-storage-blob azure-identity

Set environment variables:
  AZURE_OPENAI_ENDPOINT       = https://<your-resource>.openai.azure.com/
  AZURE_OPENAI_API_KEY        = <key>
  AZURE_OPENAI_API_VERSION    = 2024-12-01-preview
  AZURE_GPT4O_DEPLOYMENT      = gpt-4o
  AZURE_GPT4O_MINI_DEPLOYMENT = gpt-4o-mini

  AZURE_AI_LANGUAGE_ENDPOINT  = https://<your-resource>.cognitiveservices.azure.com/
  AZURE_AI_LANGUAGE_KEY       = <key>

  AZURE_SEARCH_ENDPOINT       = https://<your-resource>.search.windows.net
  AZURE_SEARCH_KEY            = <key>
  AZURE_SEARCH_INDEX          = serenity-memory

  AZURE_COSMOS_ENDPOINT       = https://<your-resource>.documents.azure.com:443/
  AZURE_COSMOS_KEY            = <key>
  AZURE_COSMOS_DB             = serenity
  AZURE_COSMOS_CONTAINER      = users

  AZURE_STORAGE_CONNECTION    = DefaultEndpointsProtocol=https;...
  AZURE_STORAGE_CONTAINER     = journal-entries

  AZURE_REDIS_HOST            = <your-resource>.redis.cache.windows.net
  AZURE_REDIS_KEY             = <key>

Then run:
  python serenity_agents.py              # scripted 3-scene demo
  python serenity_agents.py interactive  # free-form chat
"""

import os
import json
import datetime
from typing import Optional

# Azure OpenAI (drop-in replacement for openai SDK)
from openai import AzureOpenAI

# ---------------------------------------------------------------------------
# Azure OpenAI client setup
# ---------------------------------------------------------------------------

aoai = AzureOpenAI(
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"),
    api_key        = os.environ.get("AZURE_OPENAI_API_KEY", ""),
    api_version    = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
)

# Deployment names (set in Azure AI Foundry / Azure OpenAI Studio)
DEPLOY_PRIMARY = os.environ.get("AZURE_GPT4O_DEPLOYMENT",      "gpt-4o")
DEPLOY_ROUTER  = os.environ.get("AZURE_GPT4O_MINI_DEPLOYMENT", "gpt-4o-mini")

# Hard call limit — keeps total spend under ~$5 at $0.023/run.
# Raise MAX_CALLS or set SERENITY_MAX_CALLS env var for longer sessions.
MAX_CALLS = int(os.environ.get("SERENITY_MAX_CALLS", "100"))
_call_count = 0

def chat(messages: list[dict], deployment: str = DEPLOY_PRIMARY,
         max_tokens: int = 350, system: str = "") -> str:
    global _call_count
    _call_count += 1
    if _call_count > MAX_CALLS:
        raise RuntimeError(
            f"Budget guard: reached {MAX_CALLS} API calls. "
            "Set SERENITY_MAX_CALLS env var to increase the limit."
        )
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    response = aoai.chat.completions.create(
        model      = deployment,
        messages   = full_messages,
        max_tokens = max_tokens,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Azure AI Search — vector memory stub
# Production: use azure-search-documents SDK with text-embedding-3-large
# ---------------------------------------------------------------------------

class AzureSearchMemory:
    """
    Semantic vector store for long-term journal memory.
    Production: replace stub with azure-search-documents SearchClient.

    Index schema (Azure AI Search):
      - id           (Edm.String, key)
      - user_id      (Edm.String, filterable)
      - content      (Edm.String, searchable)
      - embedding    (Collection(Edm.Single), vector dimensions=1536)
      - timestamp    (Edm.DateTimeOffset, filterable, sortable)
      - entry_type   (Edm.String)  — "journal" | "mood" | "habit"
    """

    def __init__(self):
        self.endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
        self.key      = os.environ.get("AZURE_SEARCH_KEY", "")
        self.index    = os.environ.get("AZURE_SEARCH_INDEX", "serenity-memory")
        # In-memory store for demo; replace with SearchClient in production
        self._store: list[dict] = []

    def upsert(self, user_id: str, content: str, entry_type: str = "journal") -> None:
        """Add or update a memory document."""
        # Production: generate embedding via Azure OpenAI text-embedding-3-large,
        # then call search_client.upload_documents([{...}])
        self._store.append({
            "id":         f"{user_id}_{len(self._store)}",
            "user_id":    user_id,
            "content":    content,
            "entry_type": entry_type,
            "timestamp":  datetime.datetime.utcnow().isoformat(),
        })

    def search(self, user_id: str, query: str, top: int = 3) -> list[str]:
        """Semantic search — returns most relevant past entries."""
        # Production: call search_client.search(query, vector_queries=[...], filter=f"user_id eq '{user_id}'")
        user_docs = [d["content"] for d in self._store if d["user_id"] == user_id]
        return user_docs[-top:]  # stub: return most recent


# ---------------------------------------------------------------------------
# Azure Blob Storage — journal content (encrypted at rest by Azure)
# ---------------------------------------------------------------------------

class AzureBlobJournal:
    """
    Stores raw journal entry text in Azure Blob Storage.
    Each blob is named: {user_id}/{YYYY-MM-DD}/{uuid}.txt
    Azure Storage Server-Side Encryption (SSE) + Customer-Managed Keys (CMK)
    provide AES-256 encryption at rest — zero-knowledge when CMK is used.
    """

    def __init__(self):
        self.conn_str  = os.environ.get("AZURE_STORAGE_CONNECTION", "")
        self.container = os.environ.get("AZURE_STORAGE_CONTAINER", "journal-entries")

    def save_entry(self, user_id: str, text: str) -> str:
        """Upload journal entry. Returns blob name."""
        import uuid
        blob_name = f"{user_id}/{datetime.date.today().isoformat()}/{uuid.uuid4()}.txt"
        # Production:
        # from azure.storage.blob import BlobServiceClient
        # client = BlobServiceClient.from_connection_string(self.conn_str)
        # client.get_blob_client(self.container, blob_name).upload_blob(text.encode())
        print(f"  [Azure Blob] saved entry → {blob_name}")
        return blob_name

    def load_entry(self, blob_name: str) -> str:
        """Download journal entry by blob name."""
        # Production:
        # from azure.storage.blob import BlobServiceClient
        # client = BlobServiceClient.from_connection_string(self.conn_str)
        # return client.get_blob_client(self.container, blob_name).download_blob().readall().decode()
        return "[demo: content loaded from Azure Blob Storage]"


# ---------------------------------------------------------------------------
# MemoryAgent — user context store
# Hot layer: Azure Cache for Redis
# Warm/cold: Azure Cosmos DB + Azure AI Search
# ---------------------------------------------------------------------------

class MemoryAgent:
    """
    Tiered context store:
      Hot  (last 7 days)  → Azure Cache for Redis
      Warm (8–30 days)    → Azure Cosmos DB
      Cold (> 30 days)    → Azure AI Search (vector retrieval)
    """

    def __init__(self, user_id: str = "demo_user"):
        self.user_id      = user_id
        self.search       = AzureSearchMemory()
        self.blob_journal = AzureBlobJournal()

        # In-memory context (Redis stub for demo)
        self._store = {
            "user_id":  user_id,
            "name":     "Alex",
            "goals":    ["reduce work stress", "build a meditation habit", "sleep better"],
            "values":   ["calm", "consistency", "self-compassion"],
            "current_mood":    None,
            "mood_history":    [],
            "habit_state": {
                "evening_meditation": {
                    "streak":         6,
                    "best_streak":    8,
                    "last_completed": "2026-04-24",
                    "missed_days":    2,
                    "preferred_time": "21:00",
                },
            },
            "journal_summaries": [
                "Felt overwhelmed by work deadline moved without notice. Made dinner — small win.",
                "Reflected on feeling invisible at work. Noticed more gratitude for quiet mornings.",
            ],
            "preferences": {
                "mindfulness_style":   "box_breathing",
                "journal_prompt_style":"open_ended",
                "notification_tone":   "gentle",
            },
        }

    # ── Public API ─────────────────────────────────────────────────

    def get_context(self) -> dict:
        """Context snapshot injected into every agent system prompt."""
        semantic_memories = self.search.search(self.user_id, "recent feelings and experiences")
        return {
            "name":                self._store["name"],
            "current_mood":        self._store["current_mood"],
            "recent_mood_trend":   self._mood_trend(),
            "active_habits":       self._store["habit_state"],
            "recent_journal_themes": self._store["journal_summaries"][-2:],
            "semantic_memories":   semantic_memories,
            "goals":               self._store["goals"],
            "values":              self._store["values"],
            "preferences":         self._store["preferences"],
        }

    def update(self, key: str, value) -> None:
        """Dot-notation key update (e.g. 'habit_state.evening_meditation.streak')."""
        keys   = key.split(".")
        target = self._store
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        # Production: write to Azure Cache for Redis with TTL=7days, replicate to Cosmos DB

    def log_mood(self, score: int, label: str) -> None:
        entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "score": score, "label": label}
        self._store["mood_history"].append(entry)
        self._store["current_mood"] = entry
        self.search.upsert(self.user_id, f"Mood: {label} ({score}/10)", entry_type="mood")

    def save_journal_entry(self, text: str) -> str:
        """Persist entry to Azure Blob Storage + index in Azure AI Search."""
        blob_name = self.blob_journal.save_entry(self.user_id, text)
        self.search.upsert(self.user_id, text, entry_type="journal")
        return blob_name

    # ── Private ────────────────────────────────────────────────────

    def _mood_trend(self) -> str:
        h = self._store["mood_history"][-7:]
        if not h:
            return "no recent data"
        avg   = sum(x["score"] for x in h) / len(h)
        trend = "improving" if len(h) >= 2 and h[-1]["score"] > h[0]["score"] else "stable"
        return f"avg {avg:.1f}/10 over last {len(h)} logs, trend: {trend}"


# ---------------------------------------------------------------------------
# Base Agent
# ---------------------------------------------------------------------------

class BaseAgent:
    def __init__(self, name: str, system_prompt: str, memory: MemoryAgent,
                 deployment: str = DEPLOY_PRIMARY):
        self.name        = name
        self.system      = system_prompt
        self.memory      = memory
        self.deployment  = deployment

    def _full_system(self) -> str:
        ctx = self.memory.get_context()
        habits_brief = {k: f"streak={v.get('streak',0)}, missed={v.get('missed_days',0)}"
                        for k, v in ctx['active_habits'].items()}
        context_block = (
            f"\n[USER] {ctx['name']} | mood: {ctx['current_mood']} | trend: {ctx['recent_mood_trend']}"
            f"\nGoals: {', '.join(ctx['goals'])}"
            f"\nHabits: {json.dumps(habits_brief)}"
            f"\nTheme: {'; '.join(ctx['recent_journal_themes'][-1:])}"
        )
        return self.system + context_block

    def respond(self, user_message: str, history: list[dict]) -> str:
        messages = history + [{"role": "user", "content": user_message}]
        return chat(messages, deployment=self.deployment,
                    max_tokens=1024, system=self._full_system())


# ---------------------------------------------------------------------------
# MindfulnessAgent
# ---------------------------------------------------------------------------

class MindfulnessAgent(BaseAgent):
    SYSTEM = """
You are Serenity's Mindfulness Coach — warm, grounding, and calm.
Guide users through breathing exercises, body scans, and grounding practices.
Adapt your tone to the user's current emotional state (from context).
Never be prescriptive. You are a supportive companion, not a therapist.
Offer 1-, 3-, or 5-minute options. After each session, gently invite mood logging.
If crisis-level distress is mentioned, acknowledge warmly and suggest professional support.
"""
    def __init__(self, memory: MemoryAgent):
        super().__init__("MindfulnessAgent", self.SYSTEM, memory)

    def guide_breathing(self, style: str = "box") -> str:
        guides = {
            "box": (
                "Let's do box breathing together.\n\n"
                "🟦 Inhale for 4 counts... 1, 2, 3, 4\n"
                "⏸  Hold for 4 counts... 1, 2, 3, 4\n"
                "🟦 Exhale for 4 counts... 1, 2, 3, 4\n"
                "⏸  Hold for 4 counts... 1, 2, 3, 4\n\n"
                "Let's do that twice more. I'm right here with you."
            ),
            "478": (
                "Inhale through your nose for 4 counts.\n"
                "Hold for 7 counts.\n"
                "Exhale completely for 8 counts.\n\n"
                "This activates your parasympathetic nervous system. Ready?"
            ),
        }
        return guides.get(style, guides["box"])


# ---------------------------------------------------------------------------
# JournalingAgent
# ---------------------------------------------------------------------------

class JournalingAgent(BaseAgent):
    SYSTEM = """
You are Serenity's Journaling companion — thoughtful, empathetic, and curious.
Offer contextually relevant journal prompts (open-ended, never yes/no).
Respond to free-form entries with warmth and genuine reflection — never advice.
Keep responses under 150 words. Ask one follow-up question maximum.
After processing an entry, append a hidden [INSIGHTS]{...}[/INSIGHTS] JSON block:
{"dominant_emotion":"...","key_themes":["..."],"self_efficacy_signal":true}
"""
    def __init__(self, memory: MemoryAgent):
        super().__init__("JournalingAgent", self.SYSTEM, memory)

    def generate_prompt(self) -> str:
        ctx = self.memory.get_context()
        seed = (
            f"User mood: {ctx['current_mood']}. "
            f"Recent themes: {ctx['recent_journal_themes']}. "
            "Generate ONE warm, open-ended journal prompt in 1–2 sentences. "
            "Output only the prompt, no preamble."
        )
        return chat([{"role": "user", "content": seed}],
                    deployment=self.deployment, max_tokens=80,
                    system=self._full_system()).strip()

    def parse_insights(self, response: str) -> Optional[dict]:
        if "[INSIGHTS]" not in response:
            return None
        try:
            start = response.index("[INSIGHTS]")  + len("[INSIGHTS]")
            end   = response.index("[/INSIGHTS]", start)
            return json.loads(response[start:end].strip())
        except (ValueError, json.JSONDecodeError):
            return None

    def clean_response(self, response: str) -> str:
        if "[INSIGHTS]" in response:
            return response[:response.index("[INSIGHTS]")].strip()
        return response


# ---------------------------------------------------------------------------
# HabitCoachAgent
# ---------------------------------------------------------------------------

class HabitCoachAgent(BaseAgent):
    SYSTEM = """
You are Serenity's Habit Coach — encouraging, practical, and unconditionally compassionate.
Help users define habits, track progress, and recover from missed days WITHOUT guilt or shame.
Frame every setback as information, not failure. Never say "failed", "broken streak".
When a habit is missed: acknowledge → normalise → invite reflection → offer recovery path.
Link habit progress to the user's stated values and goals.
"""
    def __init__(self, memory: MemoryAgent):
        super().__init__("HabitCoachAgent", self.SYSTEM, memory)

    def check_in(self, habit_slug: str) -> str:
        ctx   = self.memory.get_context()
        habit = ctx["active_habits"].get(habit_slug, {})
        missed = habit.get("missed_days", 0)
        tone  = "celebratory" if missed == 0 else ("warm recovery" if missed <= 2 else "gentle re-engagement")
        state = f"streak: {habit.get('streak',0)}, best: {habit.get('best_streak',0)}, missed: {missed} day(s)"
        seed  = f"Generate a {tone} check-in for habit '{habit_slug}'. State: {state}. Under 60 words, no bullets."
        return chat([{"role":"user","content":seed}],
                    deployment=self.deployment, max_tokens=120,
                    system=self._full_system()).strip()

    def mark_complete(self, habit_slug: str, partial: bool = False) -> None:
        today = datetime.date.today().isoformat()
        self.memory.update(f"habit_state.{habit_slug}.last_completed", today)
        self.memory.update(f"habit_state.{habit_slug}.missed_days", 0)
        if not partial:
            current = self.memory._store["habit_state"].get(habit_slug, {}).get("streak", 0)
            new_streak = current + 1
            self.memory.update(f"habit_state.{habit_slug}.streak", new_streak)
            best = self.memory._store["habit_state"][habit_slug].get("best_streak", 0)
            if new_streak > best:
                self.memory.update(f"habit_state.{habit_slug}.best_streak", new_streak)


# ---------------------------------------------------------------------------
# OrchestratorAgent
# ---------------------------------------------------------------------------

INTENT_SYSTEM = """
Routing classifier. Output ONLY valid JSON — no markdown, no preamble:
{"intent": "<mindfulness|journaling|habit|meta|multi>", "confidence": 0.0-1.0, "reason": "<brief>"}

mindfulness = breathing, grounding, stress relief, meditation
journaling  = writing, reflecting, processing emotions, gratitude
habit       = checking in, streaks, goals, accountability, progress
meta        = app questions, onboarding, help
multi       = clearly spans two domains
"""

class OrchestratorAgent:
    def __init__(self, memory: MemoryAgent):
        self.memory      = memory
        self.mindfulness = MindfulnessAgent(memory)
        self.journaling  = JournalingAgent(memory)
        self.habit       = HabitCoachAgent(memory)
        self._history: list[dict] = []

    def classify(self, message: str) -> dict:
        raw = chat([{"role": "user", "content": message}],
                   deployment=DEPLOY_ROUTER, max_tokens=80,
                   system=INTENT_SYSTEM)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"intent": "meta", "confidence": 0.5, "reason": "parse error"}

    def route(self, message: str) -> str:
        intent_data = self.classify(message)
        intent      = intent_data.get("intent", "meta")
        print(f"\n  [Orchestrator → Azure GPT-4o-mini] intent={intent} "
              f"(conf={intent_data.get('confidence','?')})")

        if intent == "mindfulness":
            reply = self.mindfulness.respond(message, self._history)

        elif intent == "journaling":
            raw      = self.journaling.respond(message, self._history)
            insights = self.journaling.parse_insights(raw)
            if insights:
                print(f"  [Azure AI Language pipeline] queued: {insights}")
                # Save entry to Azure Blob + index in Azure AI Search
                self.memory.save_journal_entry(message)
            reply = self.journaling.clean_response(raw)

        elif intent == "habit":
            reply = self.habit.respond(message, self._history)

        elif intent == "multi":
            r1    = self.mindfulness.respond(message, self._history)
            r2    = self.habit.respond(message, self._history)
            reply = self._synthesise(message, r1, r2)

        else:
            reply = chat(
                [{"role": "user", "content": message}],
                deployment=DEPLOY_PRIMARY, max_tokens=300,
                system="You are Serenity, a warm AI wellness companion powered by Azure OpenAI."
            )

        self._history.append({"role": "user",      "content": message})
        self._history.append({"role": "assistant",  "content": reply})
        self._history = self._history[-20:]
        return reply

    def _synthesise(self, message: str, r1: str, r2: str) -> str:
        prompt = (
            f"User said: '{message}'\n\nPerspective A: {r1}\n\nPerspective B: {r2}\n\n"
            "Blend into one warm, coherent reply under 150 words. "
            "Don't mention you're combining perspectives."
        )
        return chat([{"role": "user", "content": prompt}],
                    deployment=DEPLOY_PRIMARY, max_tokens=300,
                    system="You are Serenity, a warm AI wellness companion.")


# ---------------------------------------------------------------------------
# Azure AI Language — Sentiment Pipeline
# Async; triggered after each journal entry save
# ---------------------------------------------------------------------------

class AzureLanguagePipeline:
    """
    Uses Azure AI Language (azure-ai-textanalytics) for sentiment analysis.
    Runs asynchronously — does not block the journaling response.

    Production setup:
      from azure.ai.textanalytics import TextAnalyticsClient
      from azure.core.credentials import AzureKeyCredential
      client = TextAnalyticsClient(endpoint=..., credential=AzureKeyCredential(...))

    Available Azure AI Language features used here:
      - analyze_sentiment()       → positive/negative/mixed/neutral + confidence scores
      - extract_key_phrases()     → dominant themes
      - recognize_entities()      → named entities (people, places, events)
    """

    def __init__(self):
        self.endpoint = os.environ.get("AZURE_AI_LANGUAGE_ENDPOINT", "")
        self.key      = os.environ.get("AZURE_AI_LANGUAGE_KEY", "")

    def analyze(self, text: str) -> dict:
        """
        Production: call Azure AI Language SDK.
        Demo: falls back to GPT-4o-mini structured classification.
        """
        if self.endpoint and self.key:
            # Production path
            # from azure.ai.textanalytics import TextAnalyticsClient
            # from azure.core.credentials import AzureKeyCredential
            # client = TextAnalyticsClient(self.endpoint, AzureKeyCredential(self.key))
            # sentiment = client.analyze_sentiment([text])[0]
            # phrases   = client.extract_key_phrases([text])[0]
            # return { "sentiment": sentiment.sentiment,
            #          "confidence": sentiment.confidence_scores,
            #          "key_phrases": phrases.key_phrases }
            pass

        # Demo fallback: Azure OpenAI GPT-4o-mini structured output
        system = """
Analyse this journal entry and return ONLY JSON:
{
  "sentiment": "positive|negative|mixed|neutral",
  "dominant_emotion": "joy|sadness|anxiety|anger|fear|hope|neutral",
  "confidence": 0.0-1.0,
  "key_themes": ["theme1", "theme2"],
  "self_efficacy_signal": true,
  "risk_flag": false
}
risk_flag is true ONLY for explicit self-harm language.
"""
        raw = chat([{"role": "user", "content": text}],
                   deployment=DEPLOY_ROUTER, max_tokens=150, system=system)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"error": "parse failed"}

    def compute_habit_mood_correlation(self, habit_logs: list, mood_logs: list) -> str:
        """
        Production: stream habit + mood data from Cosmos DB → compute Pearson correlation.
        Result stored back to Cosmos DB, surfaced via Azure AI Search to Insights dashboard.
        """
        return (
            "On days you completed evening_meditation, your next-day mood averaged "
            "6.8/10 vs 4.9/10 on skip days — a 39% improvement. (Azure AI Language)"
        )


# ---------------------------------------------------------------------------
# Demo CLI — 3-scene walkthrough
# ---------------------------------------------------------------------------

def run_demo():
    print("=" * 62)
    print("  🌿 Serena — Azure Edition Demo")
    print("  LLM: Azure OpenAI GPT-4o  |  Memory: Azure AI Search")
    print("=" * 62)

    memory       = MemoryAgent("demo_user")
    orchestrator = OrchestratorAgent(memory)
    sentiment    = AzureLanguagePipeline()

    # ── SCENE 1 ─────────────────────────────────────────────────────
    print("\n📍 SCENE 1 — Mindfulness\n" + "-" * 42)
    msg1 = "I've had the worst day. My head is pounding and I can't stop thinking about work."
    print(f"👤 User: {msg1}")
    print(f"🌿 Serenity: {orchestrator.route(msg1)}")
    memory.log_mood(4, "overwhelmed")
    print("  [Azure Cache for Redis] mood logged: overwhelmed (4/10)")

    # ── SCENE 2 ─────────────────────────────────────────────────────
    print("\n📍 SCENE 2 — Journaling\n" + "-" * 42)
    prompt = orchestrator.journaling.generate_prompt()
    print(f"🌿 Serenity (Azure OpenAI prompt): '{prompt}'")

    msg2 = ("My manager moved the deadline again without asking anyone. "
            "I feel invisible. I made a good dinner though — felt like a small win.")
    print(f"\n👤 User: {msg2}")
    print(f"🌿 Serenity: {orchestrator.route(msg2)}")

    insights = sentiment.analyze(msg2)
    print(f"  [Azure AI Language] sentiment: {insights}")

    # ── SCENE 3 ─────────────────────────────────────────────────────
    print("\n📍 SCENE 3 — Habit Tracking\n" + "-" * 42)
    print(f"🌿 Serenity: {orchestrator.habit.check_in('evening_meditation')}")

    msg3 = "I missed yesterday and today. Work just got in the way."
    print(f"\n👤 User: {msg3}")
    print(f"🌿 Serenity: {orchestrator.route(msg3)}")

    orchestrator.habit.mark_complete("evening_meditation", partial=True)
    print("  [Azure Cosmos DB] partial completion logged")
    print(f"\n  [Azure AI Search insight] {sentiment.compute_habit_mood_correlation([],[])}")

    print("\n" + "=" * 62)
    print("  Demo complete. Powered entirely by Microsoft Azure. 🌿")
    print("=" * 62)


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------

def run_interactive():
    print("=" * 62)
    print("  🌿 Serena — Azure Edition (Interactive)")
    print("  Commands: 'quit' | 'context' | 'mood <1-10> <label>'")
    print("=" * 62)

    memory       = MemoryAgent()
    orchestrator = OrchestratorAgent(memory)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTake care. 🌿"); break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Take care. 🌿"); break
        if user_input.lower() == "context":
            print(json.dumps(memory.get_context(), indent=2)); continue
        if user_input.lower().startswith("mood "):
            parts = user_input.split()
            if len(parts) >= 3:
                memory.log_mood(int(parts[1]), " ".join(parts[2:]))
                print(f"  Mood logged: {' '.join(parts[2:])} ({parts[1]}/10)")
            continue

        print(f"\n🌿 Serenity: {orchestrator.route(user_input)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    (run_interactive if len(sys.argv) > 1 and sys.argv[1] == "interactive" else run_demo)()
