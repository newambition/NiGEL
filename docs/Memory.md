> [!Info]
> This document details the design of the Persistent & Adaptive Memory feature. The system moves beyond simple chat history to create a long-term, evolving memory that makes the assistant more personalized and context-aware over time.

## How it Works:

1.  **Implicit Learning:** The memory system works automatically in the background. As the user interacts with the assistant, the system identifies and remembers key pieces of information (facts, names, dates, user preferences).
2.  **Attractor Formation:** Important or recurring concepts become stable "memory attractors." For example, if a user frequently discusses "Project Phoenix," it becomes a strong attractor, and new information related to it will naturally link to this memory.
3.  **Effortless Recall:** When the user asks a question, the memory system automatically identifies which attractors "resonate" with the query. This relevant information is seamlessly added to the AI's context, allowing it to provide answers that are aware of past conversations without the user needing to repeat themselves.
4.  **Evolution and Self-Repair:** The memory is not static. New information can strengthen or update existing memories. If conflicting information is provided (e.g., a deadline changes), the system updates the memory attractor and flags the old information, ensuring the assistant relies on the most current knowledge.

## Feature Justification

- **High Payoff:** This feature transforms the assistant from a stateless tool into a personalized partner that learns, adapts, and remembers. This dramatically increases its long-term value and creates a much more natural and effective user experience.
- **Managed Complexity:** The attractor model provides a robust framework for managing memory. It allows the system to start with simple fact retention and gracefully scale to a complex, interconnected knowledge graph without requiring a fundamental redesign.
- **Reduced Risk:** The memory is stored and managed locally as part of the application's state, aligning with our privacy-first principles. The primary risk is the quality of information extraction, which can be iteratively improved through prompt engineering.

## Component Breakdown

This feature is managed by the `StateManager`, which will be an evolution of the existing `Persona` class. It will contain the logic for the entire memory lifecycle.

### 1. Information Extractor
- **Responsibility:** To analyze conversations and identify information worth remembering.
- **Core Logic:** After each meaningful AI response, this component will use a meta-prompt to ask the LLM to extract key entities, facts, or preferences from the recent exchange. This uses the AI to curate its own memory.
- **Example Code (`pseudo-python`):**
```python
import json

class InformationExtractor:
    def extract_facts_from_turn(self, user_query: str, llm_response: str) -> dict:
        meta_prompt = f"""Analyze the following conversation turn.
        User: "{user_query}"
        Assistant: "{llm_response}"
        Extract key facts, entities, or preferences as a JSON object.
        Example: {{"project_name": "Phoenix", "user_preference_tone": "formal"}}
        If no new, concrete facts are present, return an empty JSON object.
        JSON:"""
        
        # This call would be made to the Gemini API
        # llm = GenerativeModel("gemini-pro")
        # extracted_json_str = llm.generate(meta_prompt)
        # For this example, we'll simulate a response.
        # In a real scenario, you would parse the actual llm response.
        if "deadline" in user_query and "monday" in user_query.lower():
            extracted_json_str = '{"project_deadline": "Monday"}'
        else:
            extracted_json_str = '{}'

        try:
            return json.loads(extracted_json_str)
        except json.JSONDecodeError:
            return {}
```

### 2. Attractor Engine
- **Responsibility:** To manage the lifecycle of memories using the principles of attractor dynamics (persistence, strengthening, decay).
- **Core Logic:** This engine manages a collection of `MemoryAttractor` objects. When new information is extracted, it either creates a new attractor or strengthens an existing one. It also handles the periodic decay of old, irrelevant memories.
- **Example Code (`pseudo-python`):**
```python
import time

class MemoryAttractor:
    def __init__(self, key: str, value: any, strength: float = 1.0):
        self.key = key
        self.values = [(value, time.time())] # Store value with timestamp
        self.strength = strength
        self.last_accessed = time.time()

    def update(self, new_value: any):
        # Add new value and check for contradictions (basic self-repair)
        if self.values[-1][0] != new_value:
            print(f"Memory Conflict for '{self.key}': old='{self.values[-1][0]}', new='{new_value}'. Updating.")
        self.values.append((new_value, time.time()))
        self.strength += 0.5 # Reinforce on update
        self.last_accessed = time.time()

    def decay(self):
        # Reduce strength over time
        self.strength *= 0.98

class AttractorEngine:
    def __init__(self):
        self.attractors = {}

    def add_or_update(self, key: str, value: any):
        if key in self.attractors:
            self.attractors[key].update(value)
        else:
            self.attractors[key] = MemoryAttractor(key, value)

    def get_relevant_memories(self, query: str) -> list:
        # V1: Simple keyword resonance
        relevant = []
        for key, attractor in self.attractors.items():
            if key.lower() in query.lower():
                relevant.append(attractor)
                attractor.last_accessed = time.time() # Reinforce on access
        return relevant

    def run_decay_cycle(self):
        keys_to_remove = []
        for key, attractor in self.attractors.items():
            attractor.decay()
            if attractor.strength < 0.1: # Threshold for forgetting
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self.attractors[key]
```

## Data Flow & Sequence

The memory lifecycle integrates seamlessly into the chat workflow:

1.  `User` sends a query.
2.  `StateManager` -> `AttractorEngine`: `get_relevant_memories(query)` to find resonant attractors.
3.  `StateManager` provides these memories to the `SynthesisService`.
4.  `SynthesisService` includes the memories in the prompt to the `Gemini API`.
5.  `Gemini API` -> `SynthesisService`: Returns a context-aware response.
6.  `SynthesisService` -> `InformationExtractor`: `extract_facts_from_turn(query, response)`.
7.  `InformationExtractor` -> `StateManager`: Returns newly extracted facts.
8.  `StateManager` -> `AttractorEngine`: `add_or_update(key, value)` for each new fact, triggering the persistence and self-repair logic.

## Technical Stack & Dependencies

- **Primary Logic:** Standard Python data structures (dictionaries, classes).
- **Persistence:** The `StateManager` will serialize the `AttractorEngine`'s state to a local file (e.g., using `pickle` or `json`) to persist memory across application restarts.
- **AI Service:** `google-generativeai` for the `InformationExtractor`'s meta-prompts.

## Risks & Mitigation Strategies

- **Risk 1: Quality of Memory Extraction.** The LLM might extract trivial or incorrect facts.
  - **Mitigation:** Start with highly constrained meta-prompts that look for very specific types of information (e.g., only facts that start with "My project is called..."). Refine these prompts over time.
- **Risk 2: Memory Clutter.** The memory could become filled with unimportant facts.
  - **Mitigation:** The `decay` mechanism is the primary defense. Memories that are not accessed or reinforced will be forgotten, keeping the memory field relevant.
- **Risk 3: Privacy.** The system stores potentially sensitive user information.
  - **Mitigation:** All memory state will be stored in a single, encrypted file within the application's local data directory. The user will be explicitly informed about the memory feature and have the ability to clear it in the settings.