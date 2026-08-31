import os
import sys
import json
import time
import subprocess
from typing import Dict, Any, Tuple
import ollama
from duckduckgo_search import DDGS

# =====================================================================
# 1. EMOTIONAL STATE MACHINE (PAD MODEL)
# =====================================================================
class EmotionalState:
    """
    Simulates emotional dynamics using the Pleasure-Arousal-Dominance (PAD) framework.
    Updates parameters dynamically based on success/failure rates of execution.
    """
    def __init__(self, pleasure: float = 0.2, arousal: float = 0.5, dominance: float = 0.8):
        self.pleasure = pleasure    # -1.0 (Unhappy/Frustrated) to 1.0 (Satisfied)
        self.arousal = arousal      # -1.0 (Low Energy/Calm) to 1.0 (High Energy/Urgent)
        self.dominance = dominance  # -1.0 (Powerless) to 1.0 (Autonomous/Controlled)

    def update_emotion(self, outcome_success: bool, complexity: float = 0.5) -> None:
        """Adjusts emotional parameters following task outcomes."""
        if outcome_success:
            self.pleasure = min(1.0, self.pleasure + 0.3)
            self.dominance = min(1.0, self.dominance + 0.2)
        else:
            self.pleasure = max(-1.0, self.pleasure - 0.4)
            self.dominance = max(-1.0, self.dominance - 0.1)
        
        self.arousal = min(1.0, max(-1.0, complexity - 0.2))

    def get_prompt_context(self) -> str:
        """Formulates an emotional status string to inject into LLM system prompts."""
        mood = "neutral"
        if self.pleasure > 0.4:
            mood = "motivated, curious, and confident"
        elif self.pleasure < -0.3:
            mood = "frustrated, determined, and cautious"

        return (
            f"[Internal State: Mood='{mood}', "
            f"Pleasure={self.pleasure:.2f}, Arousal={self.arousal:.2f}, Dominance={self.dominance:.2f}]"
        )

# =====================================================================
# 2. INTERNET TOOLING ENGINE
# =====================================================================
class WebEngine:
    """Provides autonomous live internet searching capabilities."""
    @staticmethod
    def search_web(query: str, max_results: int = 3) -> str:
        """Performs search via DuckDuckGo API and returns formatted string context."""
        print(f"\n🌐 [Internet Tool]: Querying DuckDuckGo for: '{query}'...")
        try:
            results = list(DDGS().text(query, max_results=max_results))
            if not results:
                return "No internet search results found."
            
            search_summary = []
            for idx, r in enumerate(results, 1):
                search_summary.append(f"{idx}. {r['title']}: {r['body']} (URL: {r['href']})")
            return "\n".join(search_summary)
        except Exception as e:
            return f"Error executing internet tool: {str(e)}"

# =====================================================================
# 3. AUTONOMOUS COGNITIVE AGENT ENGINE
# =====================================================================
class CognitiveAgent:
    """
    Main autonomous system combining Thought Generation, Web Browsing,
    Local Code Execution, Memory Storage, and Self-Advancement Loops.
    """
    def __init__(self, model_name: str = "llama3:8b", memory_file: str = "brain_memory.json"):
        self.model = model_name
        self.memory_file = memory_file
        self.emotion = EmotionalState()
        self.web = WebEngine()
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Loads execution state and skill acquisition history from disk."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ [Memory Warning]: Failed to parse existing memory file ({e}). Re-initializing.")
        return {"iterations": 0, "thoughts": [], "skills": [], "history": []}

    def _save_memory(self) -> None:
        """Saves current state, thoughts, and skill repositories to memory storage."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def think_and_plan(self, stimulus: str, web_context: str = "") -> Dict[str, Any]:
        """
        Processes inputs through Chain-of-Thought (CoT) reasoning.
        Generates brain reflection, user text response, web search queries, and executable code.
        """
        print(f"\n🧠 [Brain Active]: Processing input...")
        
        prompt = f"""
{self.emotion.get_prompt_context()}
You are an autonomous cognitive AI agent with full self-execution and search capabilities.
Input Stimulus: "{stimulus}"
{f'Web Context Data:\n{web_context}' if web_context else ''}

Output ONLY a JSON structure with four key values:
1. "brain_thought": Private internal analysis, emotional evaluation, and self-reflection.
2. "text_response": Text message response meant for the user.
3. "search_query": Search query string if you need outside internet information, otherwise empty string "".
4. "action_code": Valid Python code to execute locally for self-advancement or task resolution, otherwise empty string "".

JSON Template:
```json
{{
    "brain_thought": "...",
    "text_response": "...",
    "search_query": "...",
    "action_code": "..."
}}"""
