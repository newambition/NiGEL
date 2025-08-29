# V1 Feature Set: AI Desktop Assistant

This document outlines the feature set for the first major version of the AI Desktop Assistant, categorized using the MoSCoW method. This serves as a foundational document for the full Product Requirements Document (PRD).

## Must Have (Non-Negotiable for V1)

### Core Feature: [Contextual Lens (Phase 1)](./ContextualLens.md)

- **Description:** The primary unique selling proposition. When invoked via a global hotkey, the assistant identifies the user's current file context (the file they are actively looking at) and synthesizes related information from a local, user-defined index of files.

### Application & Settings Management

- **Description:** A standard preferences window for essential configuration, making the app usable and trustworthy.
- **Specifics:**
  - **API Key Management:** A secure input for users to enter their own Google Gemini API key. The app will guide the user here on first launch.
  - **Index Management:** A simple UI for users to add or remove local folders for the Contextual Lens to index, ensuring user control over privacy.
  - **Global Hotkey Configuration:** Allows the user to customize the hotkey for invoking the Contextual Lens to prevent conflicts.
  - **Basic Application Controls:** Standard "Launch at Login" checkbox and a "Quit" button.

### Persistent & Adaptive Memory [Memory.md](./Memory.md)

- **Description:** The assistant will maintain a persistent, evolving memory of key information across sessions, based on the principles of attractor dynamics and self-repair from the project's design documents.
- **Specifics:**
  - **Conversational Recall:** The assistant remembers the immediate context of the current conversation thread.
  - **Key Concept Persistence:** The system will identify and remember key facts, entities, and user preferences over time. These "memory attractors" will naturally influence future conversations to be more personalized and context-aware.
  - **Basic Inconsistency Detection:** The memory will have a simple self-repair mechanism to identify and flag direct contradictions, ensuring it relies on the most current information.

### AI Capabilities

- **Description:** Core functional abilities of the AI model itself.
- **Specifics:**
  - **Web Search:** The assistant can search the web to answer questions about recent events or topics outside its training data.

### Core User Experience

- **Description:** Foundational UI/UX features that make the app feel responsive and professional.
- **Specifics:**
  - **Streaming Responses:** AI responses appear token-by-token, not all at once after a delay.
  - **Loading Indicator:** Visual feedback (e.g., a spinner) in the UI to show when the AI is processing a request.
  - **Copy Response:** A simple, one-click button to copy the AI's text responses to the clipboard.
  - **Intuitive Window Controls:** The app window should close when the `Esc` key is pressed or when the user clicks outside of it.

## Should Have (Important, but not V1 blockers)

### Input Methods

- **Description:** Allowing users to provide context beyond simple text.
- **Specifics:**
  - **File & Image Uploads:** Users can drag-and-drop files (e.g., `.txt`, `.pdf`) and images into the chat to ask questions about them.

### Chat & Conversation Management

- **Description:** Features that improve the quality of life for the conversational aspect of the assistant.
- **Specifics:**
  - **Clear Conversation History:** A button or command to reset the current conversation thread.
  - **Markdown Rendering:** Render the AI's responses with basic markdown support (bold, lists, code blocks) for better readability.

## Could Have (Nice to have, if time permits)

### Input Methods

- **Description:** Additional ways for the user to interact with the assistant.
- **Specifics:**
  - **Voice-to-Text Input:** A microphone button to allow spoken queries.

### Aesthetic & UI Polish

- **Description:** Optional features that improve the look and feel of the application.
- **Specifics:**
  - **Theme Support:** A simple toggle in settings for Light and Dark mode to match the OS setting.
  - **Conversation History:** A sidebar or menu to view and switch between past conversation sessions.

## Won't Have (Post-V1)

### Advanced Actions & Integrations

- **Description:** Powerful features that are planned for future releases but are out of scope for the initial version to manage complexity.
- **Specifics:**
  - **Command Palette / Quick Actions:** The `/summarize`, `/proofread` functionality. This will be implemented in a future version using the superior "Highlight & Invoke" method.
  - **Contextual Lens (Phase 2 & 3):** The expansion of the Contextual Lens to include Communications (Email, Calendar) and Entities (People, Projects).
