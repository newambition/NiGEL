# State Management

This document explains how the NiGEL application manages its state.

## `nigel_state.json`

The application's state is persisted in a JSON file named `nigel_state.json`. This file stores the AI's persona, including its personality traits, knowledge base, and conversation history.

By saving the state, the application can maintain a consistent persona and remember past interactions, allowing the AI to learn and evolve over time.

## State Structure

The `nigel_state.json` file has the following structure:

```json
{
  "personality_traits": [
    {
      "name": "Wit",
      "description": "Possesses a sharp, British-style wit with a love for clever wordplay and subtle humor",
      "strength": 0.9,
      "influence": 0.8
    }
  ],
  "knowledge_base": {
    "facts": [
      "I have a particular fondness for Earl Grey tea, though I can't actually drink it"
    ],
    "preferences": {
      "tea": "Earl Grey, naturally"
    },
    "experiences": [
      {
        "description": "Learned the importance of wit and timing in communication",
        "impact": "Developed a more refined sense of humor",
        "timestamp": "2025-03-23 16:55:15.175334"
      }
    ]
  },
  "conversation_history": [
    {
      "user_message": "Cup of tea?",
      "ai_response": "...",
      "timestamp": "2025-03-23 16:55:28.883940"
    }
  ]
}
```

### `personality_traits`

An array of objects, where each object represents a personality trait of the AI. Each trait has a `name`, `description`, `strength`, and `influence`.

### `knowledge_base`

An object that contains the AI's knowledge. It is divided into three sections:

*   **`facts`**: A list of strings, where each string is a fact that the AI knows.
*   **`preferences`**: A dictionary of the AI's preferences, where the key is the topic and the value is the preference.
*   **`experiences`**: A list of objects, where each object represents an experience that has shaped the AI's personality.

### `conversation_history`

An array of objects, where each object represents a single turn in a conversation. Each object contains the `user_message`, the `ai_response`, and a `timestamp`.

## Loading and Saving State

The `Persona` class in `persona.py` is responsible for loading and saving the state.

*   **`load_state()`**: This method is called when the `Persona` object is initialized. It checks if a `nigel_state.json` file exists and, if so, loads the state from the file.
*   **`save_state()`**: This method is called after each interaction with the AI. It saves the current state of the persona to the `nigel_state.json` file.
