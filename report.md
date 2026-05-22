# HR Automation Engine: Architecture and Trade-offs Report

## 1. System Architecture
The system is designed as a modular backend using FastAPI for the REST API layer and LangGraph for the orchestration layer. 

### Core Modules:
- **FastAPI (main.py, schemas.py):** Handles HTTP requests, input validation via Pydantic, and graceful error handling. 
- **LangGraph (orchestrator.py):** Manages the state of each request, passing it through intent classification, memory injection, agent routing, and audit logging nodes.
- **Agents (agents.py):** Contains isolated sub-agent logic with built-in retry and timeout mechanisms using standard Python decorators.
- **Memory System (memory.py):** Implements a two-tier Short-Term Memory (STM) and Long-Term Memory (LTM) system.
- **Database (database.py):** Uses SQLite for an append-only audit log and memory persistence.

## 2. Intent Classification Engine
The orchestrator uses a LangGraph `StateGraph`. Incoming natural language queries are parsed in the `classify_intent` node. Based on keyword heuristics (acting as a stand-in for an LLM), it determines one of four intents: *Scheduling, Leave, Compliance, or Clarification*, and assigns a confidence score.

## 3. Memory System and Significance Scoring
The memory engine dynamically evaluates incoming data to determine if it should be retained as context for the current session (STM) or persisted as a long-term user fact (LTM).

**Significance Scoring Logic:**
- **STM (Score <= 0.7):** Ephemeral or transactional requests (e.g., keywords like "tomorrow", "cancel", "book") decrease the base score. These are useful for immediate follow-up questions but shouldn't clutter the user's permanent profile.
- **LTM (Score > 0.7):** Persistent facts (e.g., keywords like "manager", "preference", "always", "condition") increase the base score. These are promoted to LTM and always injected into the agent's prompt for that user.

*Justification:* This heuristic-based approach ensures that agents have relevant context without blowing up the context window with transactional history. In a production environment, this heuristic would be replaced by an LLM-based evaluation or vector-search similarity score.

## 4. Audit Log Enforcement
The `database.py` module exposes a `log_audit()` function that performs an `INSERT` operation. There are intentionally no `UPDATE` or `DELETE` functions for the `audit_logs` table. Every run through the LangGraph pipeline terminates at the `audit_log` node, which writes the interaction (including routing path and confidence score) to the database, ensuring a strict, append-only historical record.

## 5. Trade-offs and Considerations
- **SQLite over PostgreSQL:** SQLite was chosen to minimize dependencies and simplify the setup for this assignment. In a real-world scenario with high concurrency, a robust RDBMS like PostgreSQL should be used.
- **Heuristics vs. LLMs for Routing:** To ensure the system runs predictably and reliably without requiring active API keys for testing, keyword-based heuristics were used for intent classification and significance scoring. A production system would replace these with small, fast LLM calls (e.g., GPT-3.5 or Llama 3) or embedding models.
- **Mock Agents:** The sub-agents currently return static mocked responses. However, they include the architectural boundaries required for production (context injection, simulated timeouts, retry loops, and fallback error handling).
- **In-memory State vs. Persisted State:** LangGraph's state is currently ephemeral per request. If multi-turn conversational agents are required, the graph state should be persisted (e.g., using Redis) between API calls.

## 6. Bug Finding & Fixes
The provided workspace did not contain any starter code. Therefore, the entire system was built from scratch following the architectural guidelines provided in the prompt, ensuring no pre-existing bugs were carried over.
