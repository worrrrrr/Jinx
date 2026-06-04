"""
Jinx Memory Engine — Unified memory system for Jinx agent
===========================================================
data/memory/
├── session.json       ← SessionMemory (short-term memory, variable storage)
├── patterns.json      ← PatternMemory (learned patterns)
└── profile.json       ← UserProfileMemory (long-term user profiles)

Includes legacy functions for variable substitution needed by orchestrator.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque


# ============================================================
# PATH CONFIGURATION
# ============================================================

MEMORY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "memory"
)

SESSION_PATH = os.path.join(MEMORY_DIR, "session.json")
PATTERNS_PATH = os.path.join(MEMORY_DIR, "patterns.json")
PROFILES_DIR = os.path.join(MEMORY_DIR, "profiles")

os.makedirs(PROFILES_DIR, exist_ok=True)


# ============================================================
# LEGACY FUNCTIONS (for orchestrator.py compatibility)
# ============================================================

def extract_variables_from_result(result: Any) -> Dict[str, Any]:
    """
    Legacy: Extract single-letter variable names from math engine results.
    Example: {'x': 5, 'y': 3} -> {'x': 5, 'y': 3}
    """
    found = {}
    if isinstance(result, dict):
        for key, val in result.items():
            if isinstance(key, str) and len(key.strip()) == 1 and key.strip().isalpha():
                found[key.strip()] = val
    return found


def substitute_variables_in_text(text: str, variables: Dict[str, Any]) -> str:
    """
    Legacy: Replace variable placeholders in a math expression.
    Example: "x + 2" with {'x':5} -> "5 + 2"
    """
    if not text or not variables:
        return text
    out = text
    for name, value in variables.items():
        if not (isinstance(name, str) and len(name) == 1 and name.isalpha()):
            continue
        out = re.sub(rf"\b{re.escape(name)}\b", str(value), out)
    return out


# ============================================================
# SESSION MEMORY (Short-Term)
# ============================================================

class SessionMemory:
    """
    Short-term memory: stores recent conversation turns, temporary variables,
    and arbitrary context key-value pairs.
    Persists to disk via SESSION_PATH.
    """
    
    def __init__(self, max_turns: int = 10, persist_path: str = SESSION_PATH):
        self.max_turns = max_turns
        self.persist_path = persist_path
        
        # Conversation history (limited queue)
        self.history: deque = deque(maxlen=max_turns)
        
        # Math variables (e.g., {'x': 5})
        self._variables: Dict[str, Any] = {}
        
        # Arbitrary context (e.g., last_intent, last_domain)
        self.context: Dict[str, Any] = {}
        
        # Load existing data from disk
        self._load()
    
    def _load(self):
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for turn in data.get("history", []):
                    self.history.append(turn)
                self._variables.update(data.get("variables", {}))
                self.context.update(data.get("context", {}))
            except (json.JSONDecodeError, OSError):
                pass
    
    def _save(self):
        data = {
            "history": list(self.history),
            "variables": self._variables,
            "context": self.context,
        }
        with open(self.persist_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_turn(self, user_msg: str, jinx_response: str):
        """Record a conversation turn."""
        self.history.append({
            "user": user_msg.strip(),
            "jinx": jinx_response.strip(),
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    @property
    def variables(self) -> Dict[str, Any]:
        """Access math variables (legacy support)."""
        return self._variables
    
    def store_variables(self, new_vars: Dict[str, Any]):
        """Store or update math variables."""
        for k, v in new_vars.items():
            if isinstance(k, str) and len(k) == 1 and k.isalpha():
                self._variables[k] = v
        self._save()
    
    def get_variable(self, name: str) -> Optional[Any]:
        """Retrieve a single variable."""
        return self._variables.get(name.strip())
    
    def update_context(self, key: str, value: Any):
        """Store a context key-value pair."""
        self.context[key] = value
        self._save()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve a context value."""
        return self.context.get(key, default)
    
    def get_recent(self, n: int = 5) -> List[Dict]:
        """Return the last n conversation turns."""
        return list(self.history)[-n:]
    
    def clear(self):
        """Reset all memory (history, variables, context)."""
        self.history.clear()
        self._variables.clear()
        self.context.clear()
        self._save()


# ============================================================
# PATTERN MEMORY (Learned)
# ============================================================

class PatternMemory:
    """
    Stores aggregated usage patterns across sessions (e.g., frequent intents).
    """
    
    def __init__(self):
        self.patterns: Dict[str, Any] = {
            "common_intents": {},
            "frequent_mbti": {},
            "frequent_enneagram": {},
            "total_interactions": 0
        }
        self._load()
    
    def _load(self):
        if os.path.exists(PATTERNS_PATH):
            try:
                with open(PATTERNS_PATH, 'r', encoding='utf-8') as f:
                    self.patterns.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass
    
    def _save(self):
        with open(PATTERNS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, ensure_ascii=False, indent=2)
    
    def record_intent(self, intent: str):
        self.patterns["common_intents"][intent] = self.patterns["common_intents"].get(intent, 0) + 1
        self.patterns["total_interactions"] += 1
        self._save()
    
    def record_mbti(self, mbti_type: str):
        self.patterns["frequent_mbti"][mbti_type] = self.patterns["frequent_mbti"].get(mbti_type, 0) + 1
        self._save()
    
    def record_enneagram(self, ennea_type: str):
        self.patterns["frequent_enneagram"][ennea_type] = self.patterns["frequent_enneagram"].get(ennea_type, 0) + 1
        self._save()
    
    def get_top_intents(self, n: int = 5) -> List[tuple]:
        return sorted(self.patterns["common_intents"].items(), key=lambda x: x[1], reverse=True)[:n]
    
    def get_top_mbti(self, n: int = 3) -> List[tuple]:
        return sorted(self.patterns["frequent_mbti"].items(), key=lambda x: x[1], reverse=True)[:n]


# ============================================================
# USER PROFILE MEMORY (Long-Term)
# ============================================================

class UserProfileMemory:
    """
    Accumulates MBTI/Enneagram scores per user across sessions.
    """
    
    def __init__(self):
        self.profiles: Dict[str, Dict] = {}
    
    def _get_profile_path(self, user_id: str) -> str:
        safe_id = "".join(c for c in user_id if c.isalnum() or c in "_-")
        return os.path.join(PROFILES_DIR, f"{safe_id}.json")
    
    def get_profile(self, user_id: str) -> Dict:
        path = self._get_profile_path(user_id)
        if user_id in self.profiles:
            return self.profiles[user_id]
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                self.profiles[user_id] = profile
                return profile
            except (json.JSONDecodeError, OSError):
                pass
        # Create new
        profile = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0,
            "mbti_scores": {},
            "enneagram_scores": {},
            "cognitive_scores": {},
            "history": []
        }
        self.profiles[user_id] = profile
        return profile
    
    def _save_profile(self, user_id: str):
        profile = self.profiles.get(user_id)
        if not profile:
            return
        path = self._get_profile_path(user_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    
    def update_from_analysis(self, user_id: str, text: str, analysis: Dict):
        profile = self.get_profile(user_id)
        profile["message_count"] += 1
        profile["updated_at"] = datetime.now().isoformat()
        
        # Accumulate MBTI scores
        for pred in analysis.get("mbti_ranking", []):
            t = pred["type"]
            profile["mbti_scores"][t] = profile["mbti_scores"].get(t, 0) + pred["confidence"]
        
        # Accumulate Enneagram
        for pred in analysis.get("enneagram_ranking", []):
            t = pred["type"]
            profile["enneagram_scores"][t] = profile["enneagram_scores"].get(t, 0) + pred["confidence"]
        
        # Cognitive signature
        for func, score in analysis.get("cognitive_signature", {}).items():
            profile["cognitive_scores"][func] = profile["cognitive_scores"].get(func, 0) + score
        
        # History
        profile["history"].append({
            "text": text[:200],
            "timestamp": datetime.now().isoformat(),
            "top_mbti": analysis["mbti_ranking"][0]["type"] if analysis.get("mbti_ranking") else None
        })
        if len(profile["history"]) > 100:
            profile["history"] = profile["history"][-100:]
        
        self._save_profile(user_id)
    
    def get_best_prediction(self, user_id: str) -> Dict:
        profile = self.get_profile(user_id)
        if profile["message_count"] == 0:
            return {"best_mbti": "Unknown", "best_enneagram": "Unknown", "dominant_function": "Unknown"}
        
        mbti = max(profile["mbti_scores"].items(), key=lambda x: x[1]) if profile["mbti_scores"] else ("Unknown", 0)
        ennea = max(profile["enneagram_scores"].items(), key=lambda x: x[1]) if profile["enneagram_scores"] else ("Unknown", 0)
        func = max(profile["cognitive_scores"].items(), key=lambda x: x[1]) if profile["cognitive_scores"] else ("Unknown", 0)
        
        return {
            "user_id": user_id,
            "message_count": profile["message_count"],
            "best_mbti": mbti[0],
            "mbti_confidence": round(mbti[1] / profile["message_count"], 1) if profile["message_count"] > 0 else 0,
            "best_enneagram": ennea[0],
            "enneagram_confidence": round(ennea[1] / profile["message_count"], 1) if profile["message_count"] > 0 else 0,
            "dominant_function": func[0],
            "function_strength": round(func[1] / profile["message_count"], 2) if profile["message_count"] > 0 else 0,
        }


# ============================================================
# UNIFIED MEMORY (Optional Singleton)
# ============================================================

class JinxMemory:
    """
    Convenience wrapper for all memory subsystems.
    """
    def __init__(self):
        self.session = SessionMemory()
        self.patterns = PatternMemory()
        self.profiles = UserProfileMemory()


# ============================================================
# SINGLETON API
# ============================================================

_memory_instance = None

def get_memory() -> JinxMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = JinxMemory()
    return _memory_instance