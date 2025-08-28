import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from datetime import datetime

@dataclass
class PersonalityTrait:
    name: str
    description: str
    strength: float  # 0.0 to 1.0
    influence: float  # 0.0 to 1.0

@dataclass
class KnowledgeBase:
    facts: List[str] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    experiences: List[Dict] = field(default_factory=list)

@dataclass
class Persona:
    name: str
    description: str
    personality_traits: List[PersonalityTrait] = field(default_factory=list)
    knowledge_base: KnowledgeBase = field(default_factory=KnowledgeBase)
    conversation_history: List[Dict] = field(default_factory=list)
    learning_rate: float = 0.1
    
    def __post_init__(self):
        self.load_state()
    
    def load_state(self):
        """Load persona state from file if it exists"""
        state_file = Path(f"{self.name.lower()}_state.json")
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.personality_traits = [PersonalityTrait(**trait) for trait in state.get('personality_traits', [])]
                self.knowledge_base = KnowledgeBase(**state.get('knowledge_base', {}))
                self.conversation_history = state.get('conversation_history', [])
    
    def save_state(self):
        """Save persona state to file"""
        state_file = Path(f"{self.name.lower()}_state.json")
        state = {
            'personality_traits': [vars(trait) for trait in self.personality_traits],
            'knowledge_base': vars(self.knowledge_base),
            'conversation_history': self.conversation_history
        }
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def add_personality_trait(self, trait: PersonalityTrait):
        """Add or update a personality trait"""
        existing_trait = next((t for t in self.personality_traits if t.name == trait.name), None)
        if existing_trait:
            # Update existing trait with learning rate
            existing_trait.strength = (1 - self.learning_rate) * existing_trait.strength + self.learning_rate * trait.strength
            existing_trait.influence = (1 - self.learning_rate) * existing_trait.influence + self.learning_rate * trait.influence
        else:
            self.personality_traits.append(trait)
    
    def add_knowledge(self, fact: str):
        """Add a new fact to the knowledge base"""
        if fact not in self.knowledge_base.facts:
            self.knowledge_base.facts.append(fact)
    
    def add_preference(self, topic: str, preference: str):
        """Add or update a preference"""
        self.knowledge_base.preferences[topic] = preference
    
    def add_experience(self, experience: Dict):
        """Add a new experience to the knowledge base"""
        self.knowledge_base.experiences.append(experience)
    
    def record_conversation(self, user_message: str, ai_response: str):
        """Record a conversation exchange"""
        self.conversation_history.append({
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': str(datetime.now())
        })
        # Keep only last 100 conversations
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def get_personality_context(self) -> str:
        """Generate context about the persona's personality for the AI"""
        context = f"I am {self.name}. {self.description}\n\n"
        context += "My personality traits:\n"
        for trait in self.personality_traits:
            context += f"- {trait.name}: {trait.description} (strength: {trait.strength:.2f})\n"
        return context
    
    def get_knowledge_context(self) -> str:
        """Generate context about the persona's knowledge for the AI"""
        context = "My knowledge and preferences:\n"
        if self.knowledge_base.facts:
            context += "\nFacts I know:\n"
            for fact in self.knowledge_base.facts:
                context += f"- {fact}\n"
        
        if self.knowledge_base.preferences:
            context += "\nMy preferences:\n"
            for topic, preference in self.knowledge_base.preferences.items():
                context += f"- {topic}: {preference}\n"
        
        if self.knowledge_base.experiences:
            context += "\nMy experiences:\n"
            for exp in self.knowledge_base.experiences[-5:]:  # Last 5 experiences
                context += f"- {exp.get('description', '')}\n"
        
        return context
    
    def get_full_context(self) -> str:
        """Get complete context for the AI"""
        return f"{self.get_personality_context()}\n{self.get_knowledge_context()}"
