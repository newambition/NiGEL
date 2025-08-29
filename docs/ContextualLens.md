> [!Info]
> This feature is not an always-on, proactive assistant. Instead, it is a powerful, user-invoked tool that instantly gathers and
> synthesizes all relevant information about whatever the user is currently looking at.

## How it Works:

1.  Invocation: The user is working on something—a PDF, an email thread, a specific file in Finder, a calendar event. They press a universal system-wide hotkey (e.g., Cmd+Opt+Space).
2.  Context Identification: The assistant instantly identifies the active context (e.g., file_path: "/path/to/report.pdf", email_subject: "Project X Update", calendar_event_id: "xyz"). This uses the robust parts of the "Dynamic Context" feature (Accessibility APIs for a one-time check).
3.  Deep Search: It then feeds this context into the "Cognitive Spotlight" engine, performing a deep semantic search across all indexed local data (files, notes, other emails, etc.).
4.  Synthesis & Display: The assistant presents a clean, temporary overlay window that synthesizes the findings.

## Feature Justification

- High Payoff: It directly answers the user's most common implicit question: "What do I know about THIS?" It connects the present
  task to the user's entire digital history, providing immense value in moments of research, writing, and decision-making.
- Managed Complexity: It avoids the complexity of a fully proactive, always-on system. The logic is triggered by a single user
  action, making it simpler to develop and debug.
- Reduced Risk:
- Brittleness: By being user-invoked on a specific target, it's less reliant on constantly monitoring a changing UI. The one-time context grab is far more reliable than a persistent observer. \*
- Performance: It avoids the constant background processing and battery drain of an always-on contextual engine. It consumes resources only when you use it.
- UX: It is never intrusive or annoying because the user is always in control of its invocation.

## Component Breakdown

This feature is a composite of several distinct, modular components that work in concert.

### 1. Context Monitor (The "Dynamic Context" Trigger)
- **Responsibility:** To detect user invocation and identify the active context.
- **Core Logic:**
    - Registers and listens for a system-wide global hotkey.
    - On invocation, it identifies the frontmost application (e.g., Finder, Safari, Mail).
    - It uses macOS Accessibility APIs to query the application for its current context (e.g., the path of the selected file in Finder, the URL of the active tab in Safari).
    - It normalizes this information into a standardized context object (e.g., `{ "type": "file", "path": "/path/to/doc.pdf" }`).
    - It passes this context object to the Search Service.
- **Key Technologies:** `pynput` for hotkey listening, `pyobjc` or `py-appscript` for interacting with macOS APIs.

### 2. Indexing Service (The "Cognitive Spotlight" Knowledge Base)
- **Responsibility:** To build and maintain a searchable vector index of the user's local files.
- **Core Logic:**
    - Runs as a persistent, low-priority background thread to avoid impacting system performance.
    - Monitors user-specified folders for file changes (creations, modifications, deletions).
    - Manages a queue of files to be indexed. For each file, it:
        1.  Parses the content (e.g., using `pypdf` for PDFs).
        2.  Splits the content into meaningful text "chunks".
        3.  Uses an on-device sentence-transformer model to generate a vector embedding for each chunk.
        4.  Stores the embedding and its metadata (source file path, chunk content) in a local vector database.
- **Key Technologies:** `watchdog` for file system monitoring, `sentence-transformers` for embeddings, `LanceDB` or `ChromaDB` for the local vector store.

### 3. Search Service (The "Cognitive Spotlight" Query Engine)
- **Responsibility:** To find relevant information from the index based on the user's context.
- **Core Logic:**
    - Receives the context object from the Context Monitor.
    - Generates a vector embedding from the content of the context object (e.g., from the summary of a file).
    - Performs a vector similarity search against the index to find the most relevant text chunks.
    - Returns a structured list of the top N results, including the text and source file metadata.
- **Key Technologies:** The API of the chosen vector database (`LanceDB`, `ChromaDB`).

### 4. Synthesis Service (The AI Summarizer)
- **Responsibility:** To use the LLM to synthesize the findings into a coherent summary.
- **Core Logic:**
    - Receives the initial context and the structured search results.
    - Constructs a detailed prompt for the Gemini API, including the initial context and the retrieved information.
    - Calls the Gemini API via the existing threaded, streaming-enabled function.
    - Returns the final, human-readable text response.
- **Key Technologies:** `google-generativeai` library.

### 5. UI Manager (The Presentation Layer)
- **Responsibility:** To display the final output to the user.
- **Core Logic:**
    - Presents a clean, temporary overlay window to display the synthesized summary.
    - Handles user interactions with the result window (e.g., copy text, close window).
- **Key Technologies:** PyQt6.

## Data Flow & Sequence

The end-to-end process upon user invocation is as follows:

1.  `User` presses the global hotkey.
2.  `Context Monitor` captures the hotkey press.
3.  `Context Monitor` -> `macOS APIs`: "What is the active context?"
4.  `macOS APIs` -> `Context Monitor`: Returns file path `/path/to/doc.pdf`.
5.  `Context Monitor` -> `Search Service`: `search(context_object)`.
6.  `Search Service` -> `Vector Index`: Performs similarity search.
7.  `Vector Index` -> `Search Service`: Returns top 5 related text chunks.
8.  `Search Service` -> `Synthesis Service`: `synthesize(context, search_results)`.
9.  `Synthesis Service` -> `Gemini API`: Sends the final prompt.
10. `Gemini API` -> `Synthesis Service`: Streams back the summary.
11. `Synthesis Service` -> `UI Manager`: "Display this text."
12. `UI Manager` shows the result window to the `User`.

## Technical Stack & Dependencies

- **UI Framework:** PyQt6
- **AI Service:** Google Gemini API (`google-generativeai`)
- **System Interaction:** `pynput`, `pyobjc` / `py-appscript`
- **File Monitoring:** `watchdog`
- **Embeddings Model:** `sentence-transformers` (on-device)
- **Vector Database:** `LanceDB` or `ChromaDB` (on-device, embedded)
- **File Parsing:** `pypdf`, standard library

## Risks & Mitigation Strategies

- **Risk 1: Brittleness of Accessibility APIs.**
  - **Mitigation:** Start by supporting a small, stable set of applications (e.g., Finder). Document the supported contexts clearly. Build robust error handling for when context cannot be retrieved.
- **Risk 2: System Performance of Indexing Service.**
  - **Mitigation:** The service must run on a low-priority thread (`nice`). Indexing should be paused automatically when the user is on battery power or when high CPU usage from other apps is detected.
- **Risk 3: Quality of Search Results.**
  - **Mitigation:** The choice of embedding model and the "chunking" strategy are critical. We will need to experiment with different models and chunking methods (e.g., paragraph-based, fixed-size with overlap) to find the optimal balance.


---

Phased Implementation Plan for the "Contextual Lens"

This approach has a clear, incremental path to value.

### Phase 1: The File-Centric Lens (Low Complexity, High Initial Value)

- **Implementation:**
  - Focus solely on the file system and web context.
  - Build the background indexer for text-based files in user-specified folders.
  - Implement the hotkey to identify the currently selected file or active browser tab.
  - When invoked, perform a semantic search to find the top 3-5 most related files and display them in a simple list.

- **V1 Application Support Targets:**
    - **Tier 1: Core V1 Launch Support (Highest Priority):**
        - **Finder:** Essential for the core file-centric functionality.
        - **Safari & Google Chrome:** To provide web-based context by reading the active tab URL.
        - **Preview.app:** As the default viewer for PDFs and images, it's a critical source for file context.
        - **Visual Studio Code:** A low-risk, high-reward target to prove value for technical users via its stable APIs.
    - **Tier 2: High-Priority Fast Follows (Post-Launch Updates):**
        - **Mail.app & Notes.app:** To expand context gathering into native communication and note-taking applications.
        - **Microsoft Office Suite (Word, PowerPoint, Excel):** To support professional document workflows.

- **User Value:** Immediately useful for anyone working with documents, code, or research. "I'm looking at this proposal, show me all the
  source documents and previous drafts related to it."

### Phase 2: The Communication-Centric Lens (Medium Complexity, Massive Professional Value)

- **Implementation:**
  - Expand the indexer to include data from Mail and Calendar (tackling the permissions challenge for these key apps).
  - When invoked on an email, the Lens now finds related documents, past email threads with the same people or subject, and
    relevant upcoming calendar events.
  - When invoked on a calendar event, it pulls up the attendee list, related emails, and any documents attached or mentioned in the
    description.
- **User Value:** Transforms meeting preparation and email management. "I have a meeting with Acme Corp. Show me our last email exchange
  and the contract draft I was working on."

### Phase 3: The Entity-Centric Lens (High Complexity, Peak Value)

- **Implementation:**
  - Introduce a layer of Named Entity Recognition (NER) to the indexing process. The system now understands not just files and
    emails, but also "People," "Projects," and "Companies."
  - The Contextual Lens can be invoked on an entity. For example, highlighting a person's name ("Sarah Lee") in any application and
    pressing the hotkey.
  - The assistant presents a full "dossier": Sarah's contact info, our last 3 email exchanges, files she has sent, and upcoming
    meetings with her.
- **User Value:** This is the ultimate knowledge management tool. It creates a personal CRM and project management hub automatically from
  the user's existing data, providing 360-degree context on any topic, on demand.
