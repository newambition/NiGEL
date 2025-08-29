# Project Blueprint: AI Desktop Assistant

**Version:** 1.0
**Status:** Initial Draft

## 1. Introduction & Vision

### 1.1. Project Statement

This document outlines the product requirements and technical design for a privacy-first, AI-powered desktop assistant for macOS. The application's core purpose is to enhance user productivity by providing immediate, relevant context and powerful AI tools without requiring the user to leave their workflow. Its primary unique selling proposition is the **Contextual Lens**, a feature that proactively gathers and synthesizes information related to the user's current task.

### 1.2. Core Principles

- **Privacy-First:** All user data and content indexing will be handled on-device. Cloud services are only used for explicit, user-initiated AI model queries.
- **User in Control:** The assistant is invoked by the user (e.g., via hotkey). It does not perform distracting, unsolicited proactive actions.
- **Context-Aware:** The assistant is designed to understand the user's immediate context (e.g., the file they are viewing) to provide hyper-relevant assistance.
- **Extensible:** The system is designed with a modular architecture to allow for the addition of new features and capabilities over time.

---

## 2. V1 Product Requirements

### 2.1. Feature Set (MoSCoW)

This section summarizes the V1 feature set. For the full, detailed list, please refer to [feature-set.md](./feature-set.md).

- **Must Have:**
  - Core Feature: [Contextual Lens (Phase 1)](./ContextualLens.md)
  - Application & Settings Management
  - Persistent & Adaptive Memory [Memory.md](./Memory.md)
  - AI Capabilities: Web Search
  - Core UX: Streaming Responses, Loading Indicators, etc.
- **Should Have:**
  - Input Methods: File & Image Uploads
  - Chat Management: Clear History, Markdown Rendering
- **Could Have:**
  - Input Methods: Voice-to-Text
  - UI Polish: Theme Support, Conversation History
- **Won't Have (Post-V1):**
  - Command Palette / Quick Actions
  - Contextual Lens (Phases 2 & 3)

### 2.2. Key User Stories (V1)

- **Contextual Lens:** "As a researcher reviewing a document, I can press a hotkey to instantly see a summary of related documents from my local folders, so that I can gather insights and references without manually searching."
- **Memory:** "As a project manager, I can mention a key project deadline in a conversation, and the assistant will remember this fact in future conversations to provide more relevant answers."
- **Settings:** "As a new user, I am guided to a settings screen on first launch, so that I can enter my API key and select the folders I want the assistant to index."
- **Web Search:** "As a user, I can ask about a recent news event, and the assistant will use a web search to provide a current, up-to-date answer."

---

## 3. System Architecture & Design

This section outlines the technical architecture, evolving from the [current-architecture.md](./current-architecture.md) to the new proposed architecture. The design
defined in [chatbotschema.yaml](./chatbotschema.yaml)

### 3.1. High-Level Architecture

The system is composed of several distinct services orchestrated by the main application process. This modular design allows for clear separation of concerns.

```
+--------------------------------------------------------------------+
|                           User (macOS)                             |
+--------------------------------------------------------------------+
     |        ^         |         ^          |           ^
     | Hotkey | UI      |         |          |           |
     v        | Events  v         |          |           |
+-----------------------+------------------+-------------------------+
|      UI Manager       |  Context Monitor |   Indexing Service      |
| (PyQt6, Main Thread)  | (Listener Thread)|  (Background Thread)    |
+-----------------------+------------------+-------------------------+
     |         |         |         ^          |           |
     | Display | Get     |         |          |           |
     | Results | Context |         |          |           |
     v         v         v         |          |           |
+--------------------------------------------------------------------+
|                 Orchestrator / Main Application Logic              |
+--------------------------------------------------------------------+
     |         ^         |         ^          |           ^
     | Query   | Results |         |          |           |
     v         |         v         |          |           |
+-----------------------+------------------+-------------------------+
|     Search Service    | Synthesis Service|      State Manager      |
| (Vector Search)       | (Gemini API)     | (Index/Config/Memory)   |
+-----------------------+------------------+-------------------------+
```

### Proposed Architecture that uses the current architecture as a starting point

- `main.py` (Orchestrator):

* Remains the entry point.
* Will be responsible for initialising and starting the new ContextMonitor and IndexingService.
* Its role expands from just managing a chat window to orchestrating all background services.

- `persona.py` -> `StateManager.py` (Evolved):

* The Persona class is refactored into a more generic StateManager.
* It will manage not only the conversation history but also:
  - The file path to the local vector database (e.g., index.lancedb).
  - The state of the index (e.g., last indexed timestamp).
  - User preferences for the Contextual Lens.

- `ContextMonitor.py` (New Module):

* A new, standalone component.
* Responsibility: To be the "eyes" of the application.
* Functionality:
  - Registers and listens for a global system-wide hotkey.
  - When the hotkey is pressed, it uses macOS Accessibility APIs to identify the active window and focused element (e.g., the path
    to a selected file in Finder).
  - It emits a signal (e.g., contextAcquired(context_info)) for the main application to act upon.

- `IndexingService.py` (New Module):

* A new, standalone component that runs in its own background thread (using the same QThread pattern).
* R esponsibility: To build and maintain the search index.
* Functionality:
  - On startup, it loads the index from the StateManager.
  - It has a queue for indexing tasks. It can be triggered to scan directories, generate embeddings for new files, and add them to
    the vector database.
  - Provides a method search(context_embedding) that returns a list of relevant results.

- `ClippyDropdown` (UI - Adapted):

* The hotkey signal from the ContextMonitor will trigger the UI to show.
* Instead of just a chat input, it will now have a mode to display the synthesized results from the Contextual Lens.
* The core ask_gemini function is repurposed: it's now the final step, synthesize_results(context, search_results), which takes the
  initial context and the search findings to generate the final summary for display.

### 3.2. Component Breakdown

- **UI Manager:** Renders the PyQt6 interface. No change from the initial design.

- **Context Monitor:** Listens for the global hotkey and uses macOS APIs to get the user's active context. No change from the initial design.

- **Indexing Service:** A background thread that monitors folders, parses files, and creates vector embeddings. We can enhance this by thinking of the indexed items not just as data, but as potential **memory attractors** within a semantic field.

- **Search Service:** Queries the vector index. This service's function is enhanced to be understood as measuring the **resonance** between the user's current context and the document **attractors** stored in the index, returning the items with the highest resonance score.

- **Synthesis Service (Enhanced):** This component becomes a **Cognitive Tool Executor**.

  - **Token Budgeting:** Before every API call, it checks the total prompt size. If it exceeds the model's limit, it applies `history.summarize` or `priority_pruning` rules from the schema to compress the context automatically.
  - **Structured Prompts:** It wraps requests in formal **Protocol Shells**. For the Contextual Lens, it will use a `research.synthesize` protocol, providing the LLM with a structured task that improves reliability and consistency of the output.

- **State Manager (Enhanced):** An evolution of the `Persona` class, this component now acts as a comprehensive **Memory Manager**.
  - **Tiered Memory:** It explicitly manages **Episodic** (conversation history), **Semantic** (the Attractor Engine for facts), and **Key-Value** (user settings) memory.
  - **Attractor Engine:** Manages the lifecycle of semantic memories. It forms new **attractors** from important, recurring information. Attractor `strength` is reinforced through use and `decays` over time, allowing the system to forget irrelevant details.
  - **Sleep Consolidation:** Implements a periodic process (e.g., on app launch) to run a consolidation cycle, strengthening related memories and pruning weak ones to maintain a coherent knowledge base.

### 3.3. Data Models

- **Context Object:** A standardized JSON object passed from the `ContextMonitor`.
  ```json
  {
    "type": "file",
    "source_app": "Finder",
    "content_path": "/Users/user/Documents/report.pdf"
  }
  ```
- **Vector Index Metadata:** Each vector in the index will be stored with metadata.
  ```json
  {
    "source_file": "/Users/user/Documents/report.pdf",
    "chunk_id": 12,
    "text_content": "The quick brown fox...",
    "last_modified": "2023-10-27T10:00:00Z"
  }
  ```
- **Memory Attractor Object:** The structure for a persistent memory item in the `StateManager`.
  ```json
  {
    "key": "Project Phoenix Deadline",
    "values": [("2025-12-15", 1729987200)],
    "strength": 1.5,
    "last_accessed": 1730073600
  }
  ```

### 3.4. Technical Stack

(No changes from the previous version)

- **UI Framework:** PyQt6
- **AI Service:** Google Gemini API (`google-generativeai`)
- **System Interaction:** `pynput`, `pyobjc` / `py-appscript`
- **File Monitoring:** `watchdog`
- **Embeddings Model:** `sentence-transformers` (on-device)
- **Vector Database:** `LanceDB` or `ChromaDB` (on-device, embedded)
- **File Parsing:** `pypdf`, standard library

---

## 4. Phased Development Roadmap

This roadmap integrates the feature rollout from `feature-set.md` with the phased implementation plan from `ContextualLens.md`.

### 4.1. Version 1.0 (MVP)

- **Goal:** Deliver the core value of the Contextual Lens and a robust, usable assistant.
- **Features:**
  - All **Must Have** features from `feature-set.md`.
  - This includes **Phase 1 (File-Centric)** of the Contextual Lens.

### 4.2. Version 1.1 (First Major Update)

- **Goal:** Expand input methods and improve quality of life.
- **Features:**
  - All **Should Have** features from `feature-set.md`.
  - This includes adding File & Image upload capabilities and improving chat management.

### 4.3. Future Versions (Backlog)

- **Goal:** Explore advanced features and UI polish based on user feedback.
- **Features:**
  - All **Could Have** and **Won't Have (Post-V1)** features.
  - This includes the **Phase 2 & 3** of the Contextual Lens and the **Command Palette**.

---

## 5. Risks & Open Questions

This section tracks known risks, primarily drawn from the analysis in `ContextualLens.md`.

- **Risk 1: Brittleness of Accessibility APIs.**
  - **Mitigation:** For V1, limit support to a small, stable set of applications (Finder). Build robust error handling for when context cannot be retrieved. Add more applications incrementally.
- **Risk 2: System Performance of Indexing Service.**
  - **Mitigation:** The service must run on a low-priority thread. Implement logic to pause indexing when the user is on battery power or when high CPU usage from other apps is detected.
- **Risk 3: Quality of Search Results.**
  - **Mitigation:** The choice of embedding model and the text "chunking" strategy are critical. Allocate time for experimentation with different models and chunking methods to find the optimal balance for quality.
- **Risk 4: Permissions for Future Data Sources.**
  - **Mitigation:** Phase 2 (Email/Calendar indexing) will require explicit and carefully handled macOS permissions. This is a known hurdle and will require dedicated research and a secure implementation.
