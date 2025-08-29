# AI Desktop Assistant - V1.0 MVP Task Checklist

This document provides a detailed, phased checklist for the development of Version 1.0. Each task should be checked off upon completion to track progress towards the MVP.

---

## Phase 0: Project Setup & Core Foundation

**Goal:** Establish a stable codebase, refactor the initial application, and set up all necessary dependencies.

- [ ] **Environment Setup:**
    - [ ] Create a new Python virtual environment.
    - [ ] Install all core dependencies as listed in `ProjectBlueprint.md` (PyQt6, google-generativeai, sentence-transformers, pynput, watchdog, etc.).
- [ ] **Initial Code Refactoring:**
    - [ ] Rename `persona.py` to `StateManager.py`.
    - [ ] Refactor the `Persona` class into a `StateManager` class, creating stub methods for future state management (index path, memory, settings).
    - [ ] Update `main.py` to import and initialize the new `StateManager`.
- [ ] **Logging:**
    - [ ] Implement a basic, centralized logging system to record application events, errors, and key operations.

### Acceptance Criteria:
- [ ] The application can be launched from a clean checkout without any errors.
- [ ] All dependencies are managed in a `requirements.txt` file.
- [ ] The main application window appears on launch.
- [ ] A log file is created on startup and captures initial messages.

---

## Phase 1: Foundational Services (Backend Implementation)

**Goal:** Build the core non-UI services for memory, indexing, and search.

- [ ] **`StateManager` Implementation:**
    - [ ] Implement saving and loading the entire application state to a local, encrypted file.
    - [ ] Implement the `MemoryAttractor` class as defined in `Memory.md`.
    - [ ] Implement the `AttractorEngine` class within the `StateManager` to manage the lifecycle of memory attractors (add, update, decay).
- [ ] **`IndexingService` Implementation:**
    - [ ] Create the `IndexingService` class that runs in a dedicated `QThread`.
    - [ ] Implement file system monitoring using `watchdog` to watch folders specified in the `StateManager`.
    - [ ] Implement file parsers for `.txt`, `.md`, and `.pdf` (`pypdf`).
    - [ ] Implement text chunking logic to split large documents.
    - [ ] Integrate `sentence-transformers` to generate vector embeddings for each text chunk.
    - [ ] Implement logic to store embeddings and their metadata in a local vector database (`LanceDB` or `ChromaDB`).
- [ ] **`SearchService` Implementation:**
    - [ ] Implement the `search(query_vector)` method.
    - [ ] The method should perform a vector similarity search on the index and return the top N matching results.

### Acceptance Criteria:
- [ ] The `StateManager` can successfully save its state to a file and load it back correctly on application restart.
- [ ] Unit tests confirm the `AttractorEngine` can add, update, and decay memories as designed.
- [ ] The `IndexingService` thread successfully detects file changes in a test folder.
- [ ] The service correctly parses text and PDF files, generating and storing their embeddings in the local vector database.
- [ ] The `SearchService` can be called with a test vector and returns an ordered list of relevant results from the index.

---

## Phase 2: AI & Logic Integration

**Goal:** Connect the backend services to the Gemini API and implement the core AI logic.

- [ ] **`SynthesisService` (Cognitive Tool Executor):**
    - [ ] Implement the Token Budgeting logic to check prompt size and apply summarization rules if the context is too large.
    - [ ] Create a structured prompt function for the `research.synthesize` protocol to be used by the Contextual Lens.
    - [ ] Create a structured prompt function for a standard conversational query.
- [ ] **`InformationExtractor` (Memory Curation):**
    - [ ] Implement the meta-prompt logic within the `SynthesisService` to extract key facts from conversations.
    - [ ] Connect this extractor to the `StateManager` to feed it new `MemoryAttractor` data.
- [ ] **Web Search Integration:**
    - [ ] Integrate a web search API (e.g., Google Custom Search API).
    - [ ] Enhance the `SynthesisService` to detect when a user query requires real-time information.
    - [ ] Implement the logic to perform a web search, inject the results into the prompt context, and generate a synthesized answer.

### Acceptance Criteria:
- [ ] The `SynthesisService` successfully returns a response from the Gemini API for a simple query.
- [ ] The `InformationExtractor` correctly identifies and extracts a key fact from a test conversation and saves it via the `StateManager`.
- [ ] A query like "What is the news about Gemini today?" triggers the web search, and the final response includes information from the search results.
- [ ] The `StateManager` can demonstrate that a relevant `MemoryAttractor` is retrieved and added to the prompt context for a relevant query.

---

## Phase 3: UI & Feature Connection

**Goal:** Build the user-facing interfaces and connect them to the backend services.

- [ ] **Settings & Preferences Window:**
    - [ ] Design and build the UI for the settings window using PyQt6.
    - [ ] Connect the UI elements to the `StateManager` to manage:
        - [ ] API Key (save/load).
        - [ ] Indexed Folders (add/remove).
        - [ ] Global Hotkey configuration.
        - [ ] "Launch at Login" preference.
- [ ] **Main Chat Window & Core UX:**
    - [ ] Implement the logic to stream responses token-by-token in the chat display.
    - [ ] Connect the UI's loading indicator to the start and end signals of the `SynthesisService` worker thread.
    - [ ] Add a "Copy" button to each AI message bubble.
    - [ ] Implement the `Esc` key press and "click-away" events to hide the main window.
- [ ] **Contextual Lens Feature Integration:**
    - [ ] Implement the `ContextMonitor` class in a `QThread`.
    - [ ] Implement the global hotkey listener using `pynput`.
    - [ ] Implement the macOS-specific code (`pyobjc` or `py-appscript`) to get the active application and selected file path (for V1, focus on Finder).
    - [ ] Connect the `ContextMonitor`'s `contextAcquired` signal to the main orchestrator.
    - [ ] Wire up the full end-to-end data flow for the Contextual Lens as defined in the blueprint.
    - [ ] Create the specific UI view within the main window to display the Contextual Lens results.

### Acceptance Criteria:
- [ ] All fields in the Settings window correctly load from and save to the `StateManager`'s state file.
- [ ] The main chat window displays AI responses as they are being generated.
- [ ] The UI remains fully responsive (no freezing) while the AI is thinking.
- [ ] Pressing the configured global hotkey while a file is selected in Finder successfully triggers the Contextual Lens and displays a relevant summary in the UI.

---

## Phase 4: Packaging & Finalization

**Goal:** Prepare the application for distribution and release.

- [ ] **First-Run Experience:**
    - [ ] Create a welcome screen or dialog that guides the new user to the settings page to enter their API key and select folders.
- [ ] **Application Packaging:**
    - [ ] Configure `py2app` or a similar tool to build a standalone macOS `.app` bundle.
    - [ ] Ensure all on-device models and dependencies are included in the bundle.
- [ ] **Documentation & Testing:**
    - [ ] Create a user-facing `README.md` with clear installation and usage instructions.
    - [ ] Perform end-to-end testing on all V1 "Must Have" features.
    - [ ] Create a release tag in the version control system.

### Acceptance Criteria:
- [ ] A distributable `.app` bundle is successfully created.
- [ ] The application can be launched and run on a clean macOS machine without manual dependency installation.
- [ ] The first-launch experience successfully guides a user to a fully configured and working state.
- [ ] All V1 features work as described in the user stories in the `ProjectBlueprint.md`.