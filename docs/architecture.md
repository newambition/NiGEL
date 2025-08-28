# Architecture

This document provides a detailed overview of the NiGEL project's architecture.

## High-Level Overview

The application is built using a combination of PyQt6 for the graphical user interface and the Google Gemini API for the conversational AI.

The architecture can be broken down into three main components:

1.  **User Interface (UI):** The UI is built with PyQt6 and consists of a system tray icon and a chat window.
2.  **AI Persona:** The AI's personality, knowledge base, and conversation history are managed by the `Persona` class.
3.  **AI Interaction:** The application interacts with the Google Gemini API to generate responses to user messages.

## Core Components

### `main.py`

This file is the entry point of the application. It is responsible for:

*   Initializing the PyQt6 application.
*   Creating the system tray icon and the chat window.
*   Handling user input and displaying the conversation.
*   Calling the `ask_gemini` function to get responses from the AI.

### `persona.py`

This file defines the data structures for the AI's persona. It contains the following classes:

*   **`PersonalityTrait`**: Represents a single personality trait of the AI.
*   **`KnowledgeBase`**: Stores facts, preferences, and experiences for the AI.
*   **`Persona`**: Encapsulates the entire persona of the AI, including its personality traits, knowledge base, and conversation history. It also provides methods for saving and loading the persona's state.

### `ask_gemini(question)`

This function in `main.py` is responsible for interacting with the Google Gemini API. It performs the following steps:

1.  Retrieves the full context of the AI's persona using the `get_full_context()` method of the `Persona` class.
2.  Constructs a prompt that includes the persona context and the user's question.
3.  Sends the prompt to the Gemini API using the `google-generativeai` library.
4.  Records the conversation in the persona's history.
5.  Saves the updated persona state.
6.  Returns the AI's response to be displayed in the UI.

## UI Structure

The UI is composed of two main classes:

*   **`ClippyApp`**: The main application class that inherits from `QApplication`. It manages the system tray icon and its context menu.
*   **`ClippyDropdown`**: A `QMainWindow` that serves as the chat window. It contains all the UI elements for the chat interface, such as the conversation display, input field, and send button.

## Threading Model

To ensure the UI remains responsive while waiting for a response from the Gemini API, the application uses a separate thread to call the `ask_gemini` function. The `ClippyDropdown` class uses `pyqtSignal` to communicate between the worker thread and the main UI thread, allowing for safe updates to the UI with the AI's response.
