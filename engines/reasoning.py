# engines/reasoning.py (อัปเดต PlanOutput และโครงสร้างส่งออกแผนงาน)

import re
from dataclasses import dataclass, asdict
from typing import Dict, Any, List

@dataclass(frozen=True)
class PlanOutput:
    action: str  # 👈 เพิ่มฟิลด์ประสานงานคำสั่งหลักไปยังเครื่องมือย่อย
    intent: str
    domain: str
    tasks: List[str]
    entities: List[str]
    topic: str
    confidence: float
    status: str
    metadata: Dict[str, Any]
    response_hint: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReasoningEngine:
    def __init__(self):
        self.strategy_matrix = {
            ("task:solve", "math"): ["validate_numbers", "parse_expression", "compute_math", "format_result"],
            ("task:edit", "file"): ["check_file_exists", "backup_file", "update_file_content", "verify_change"],
            ("task:delete", "file"): ["confirm_permission", "check_file_exists", "delete_file", "log_action"],
            ("task:copy", "file"): ["check_source_exists", "validate_destination", "copy_file", "verify_copy"],
            ("task:move", "file"): ["check_source_exists", "validate_destination", "move_file", "cleanup_source"],
            ("task:execute", "code"): ["check_file_exists", "validate_script", "run_script", "capture_output"],
            ("task:debug", "code"): ["parse_error_log", "identify_issue", "suggest_fix", "generate_patch"],
            ("task:search", "web"): ["validate_query", "fetch_results", "rank_relevance", "summarize"],
            
            ("chat:greet", "conversation"): ["detect_tone", "select_greeting", "personalize_response"],
            ("chat:farewell", "conversation"): ["detect_context", "select_farewell", "offer_future_help"],
            ("chat:gratitude", "conversation"): ["acknowledge_thanks", "humble_response", "offer_more"],
            ("chat:apology", "conversation"): ["accept_apology", "reassure", "move_forward"],
            ("chat:chitchat", "conversation"): ["detect_topic", "retrieve_smalltalk", "add_personality", "engage"],
            ("chat:emotion", "conversation"): ["detect_sentiment", "validate_feeling", "respond_empathy", "offer_support"],
            ("chat:joke", "conversation"): ["select_humor_type", "fetch_joke", "deliver_with_timing"],
            
            ("qa:what", "qa"): ["parse_question", "search_knowledge", "extract_definition", "format_answer"],
            ("qa:why", "qa"): ["parse_question", "find_cause", "explain_reasoning", "format_answer"],
            ("qa:how", "qa"): ["parse_question", "find_procedure", "step_by_step", "format_answer"],
            ("qa:explain", "qa"): ["parse_question", "gather_context", "elaborate", "format_answer"],
        }
        
        self.fallback_plans = {
            "unknown": ["log_input", "request_clarification"],
            "default": ["analyze_input", "route_to_appropriate_handler"]
        }
        
        self.context_rules = [
            {"if_intent_contains": "delete", "if_entity_has": "file", "then_add_task": "confirm_with_user", "priority": "high"},
            {"if_domain": "math", "if_confidence_below": 0.7, "then_add_task": "double_check_calculation", "priority": "normal"},
            {"if_intent_contains": "chat:", "if_topic_contains_any": ["เครียด", "เหนื่อย", "เศร้า"], "then_add_task": "respond_empathy_first", "priority": "empathy_first"},
        ]

    def plan(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        # สกัดข้อมูลแผนงานหลัก
        action = perception.get("action", "noop")  # 👈 ดึงคำสั่งจาก Perception
        intent = perception.get("intent", "unknown")
        domain = perception.get("domain", "general")
        entities = perception.get("entities", [])
        topic = perception.get("topic", "")
        confidence = perception.get("confidence", 0.0)
        
        is_chitchat = perception.get("is_chitchat", False)
        is_question = perception.get("is_question", False)
        
        task_sequence = self._find_strategy(intent, domain)
        task_sequence = self._apply_context_rules(task_sequence, intent, domain, entities, topic, confidence)
        response_hint = self._generate_response_hint(intent, topic, len(entities) > 0)
        
        # แนบคำสั่งรันหลักเข้าสู่กระบวนการ PlanOutput
        plan_output = PlanOutput(
            action=action,  # 👈 จัดส่งลงในแผนงานมาตรฐาน
            intent=intent,
            domain=domain,
            tasks=task_sequence,
            entities=entities,
            topic=topic,
            confidence=confidence,
            status=self._determine_status(task_sequence, confidence),
            metadata={
                "is_chitchat": is_chitchat,
                "is_question": is_question,
                "requires_user_input": self._needs_user_input(intent, task_sequence),
                "priority": self._calc_priority(intent, domain, topic)
            },
            response_hint=response_hint
        )
        
        return plan_output.to_dict()

    def _find_strategy(self, intent: str, domain: str) -> List[str]:
        if (intent, domain) in self.strategy_matrix:
            return list(self.strategy_matrix[(intent, domain)])
        
        for (intent_pattern, domain_key), tasks in self.strategy_matrix.items():
            if domain == domain_key and isinstance(intent_pattern, str) and re.match(intent_pattern, intent):
                return list(tasks)
        
        intent_base = intent.split(":")[-1] if ":" in intent else intent
        return list(self.fallback_plans.get(intent_base, self.fallback_plans["default"]))

    def _apply_context_rules(self, tasks: List[str], intent: str, domain: str, 
                             entities: List[str], topic: str, confidence: float) -> List[str]:
        modified_tasks = tasks.copy()
        for rule in self.context_rules:
            triggered = True
            if "if_intent_contains" in rule and rule["if_intent_contains"] not in intent:
                triggered = False
            if "if_domain" in rule and rule["if_domain"] != domain:
                triggered = False
            if "if_entity_has" in rule and not any(rule["if_entity_has"] in ent for ent in entities):
                triggered = False
            if "if_confidence_below" in rule and confidence >= rule["if_confidence_below"]:
                triggered = False
            if "if_topic_contains_any" in rule:
                topic_lower = topic.lower()
                if not any(kw in topic_lower for kw in rule["if_topic_contains_any"]):
                    triggered = False
                    
            if triggered:
                task_to_add = rule["then_add_task"]
                if task_to_add not in modified_tasks:
                    if rule.get("priority") == "empathy_first":
                        modified_tasks.insert(0, task_to_add)
                    else:
                        modified_tasks.append(task_to_add)
                        
        return modified_tasks

    def _determine_status(self, tasks: List[str], confidence: float) -> str:
        if not tasks or tasks == self.fallback_plans["default"]:
            return "ambiguous"
        if confidence < 0.5:
            return "low_confidence"
        if "request_clarification" in tasks:
            return "awaiting_input"
        return "ready"

    def _needs_user_input(self, intent: str, tasks: List[str]) -> bool:
        return intent in ["unknown", "clarify"] or any(t in tasks for t in ["request_clarification", "confirm_with_user"])

    def _calc_priority(self, intent: str, domain: str, topic: str) -> str:
        if domain in ["system", "security"]:
            return "high"
        if "chat:emotion" in intent and any(w in topic.lower() for w in ["เครียด", "เศร้า", "เหนื่อย"]):
            return "high"
        if "delete" in intent:
            return "high"
        if intent.startswith(("qa:", "task:")):
            return "medium"
        return "low"

    def _generate_response_hint(self, intent: str, topic: str, has_entities: bool) -> Dict[str, Any]:
        hint = {"style": "neutral", "tone": "friendly", "length": "medium"}
        if "greet" in intent:
            hint.update({"style": "warm", "emoji": True, "length": "short"})
        elif "farewell" in intent:
            hint.update({"style": "warm", "emoji": True, "length": "short", "include_future": True})
        elif "emotion" in intent:
            hint.update({"style": "empathetic", "tone": "caring", "length": "medium", "avoid_solutions": True})
        elif "joke" in intent:
            hint.update({"style": "playful", "tone": "humorous", "length": "short"})
        elif intent.startswith("qa:"):
            hint.update({"style": "informative", "tone": "helpful", "include_sources": True})
        elif "chitchat" in intent:
            hint.update({"style": "casual", "tone": "conversational", "ask_back": True})
        if has_entities:
            hint["mention_entities"] = True
        return hint