"""
State Flow Engine - ระบบจัดการการถามตอบตาม Template
อ่านไฟล์ template_*.json และดำเนินการถามตอบแบบมีขั้นตอน
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class StateFlowEngine:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates = {}
        self.active_sessions = {}  # เก็บสถานะการสนทนาของแต่ละผู้ใช้
        self._load_all_templates()
    
    def _load_all_templates(self):
        """โหลดทุกไฟล์ template ที่มีอยู่ในโฟลเดอร์"""
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for file_path in self.templates_dir.glob("template_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_name = file_path.stem.replace('template_', '')
                    self.templates[template_name] = template_data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    def _detect_intent(self, user_input: str) -> Optional[str]:
        """ตรวจจับความตั้งใจจากคำพูดผู้ใช้และจับคู่กับ template"""
        user_input_lower = user_input.lower()
        
        # คำค้นหาสำหรับแต่ละ template
        intent_map = {
            'ai_project': [
                'ai', 'artificial intelligence', 'agent', 'rag', 'neuro-symbolic', 
                'machine learning', 'llm', 'ollama', 'fastapi', 'hugging face',
                'โปรเจกต์ ai', 'เอไอ', 'แชทบอท', 'ผู้ช่วยอัจฉริยะ'
            ],
            'web_dev': [
                'web', 'website', 'frontend', 'backend', 'react', 'vue', 'angular',
                'django', 'flask', 'fastapi', 'node.js', 'express', 'html', 'css',
                'javascript', 'typescript', 'ecommerce', 'เว็บ', 'เว็บไซต์', 'หน้าเว็บ'
            ],
            'data_science': [
                'data', 'analytics', 'visualization', 'pandas', 'numpy', 'scikit-learn',
                'jupyter', 'matplotlib', 'seaborn', 'sql', 'database', 'etl',
                'ข้อมูล', 'วิเคราะห์ข้อมูล', 'ดาต้า', 'กราฟ', 'สถิติ'
            ],
            'mobile_app': [
                'mobile', 'app', 'ios', 'android', 'flutter', 'react native', 'swift',
                'kotlin', 'xamarin', 'ionic', 'แอป', 'มือถือ', 'แอพพลิเคชัน'
            ],
            'devops_cloud': [
                'devops', 'cloud', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
                'ci/cd', 'jenkins', 'gitlab', 'terraform', 'ansible', 'serverless',
                'deployment', 'container', 'ไมโครเซอร์วิส', 'คลาวด์', 'เซิร์ฟเวอร์'
            ],
            'content_creator': [
                'content', 'creator', 'youtube', 'tiktok', 'instagram', 'facebook',
                'video', 'podcast', 'streaming', 'twitch', 'influencer', 'vlog',
                'คอนเทนต์', 'ครีเอเตอร์', 'ยูทูปเบอร์', 'วิดีโอ', 'ไลฟ์สด', 'โพสต์'
            ]
        }
        
        # ตรวจสอบแต่ละ intent
        for intent, keywords in intent_map.items():
            if intent in self.templates:  # เฉพาะ template ที่มีอยู่จริง
                for keyword in keywords:
                    if keyword in user_input_lower:
                        return intent
        
        return None
    
    def process(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """
        ประมวลผลคำพูดผู้ใช้และคืนค่าผลลัพธ์
        """
        # 1. ตรวจจับ intent
        detected_intent = self._detect_intent(user_input)
        
        if not detected_intent:
            return {
                "status": "no_match",
                "message": "ขอโทษครับ ผมยังไม่เข้าใจว่าคุณต้องการทำอะไร ช่วยระบุรายละเอียดเพิ่มเติมได้ไหมครับ? เช่น 'อยากทำเว็บ', 'สร้างแอปมือถือ', 'วิเคราะห์ข้อมูล'",
                "suggestions": list(self.templates.keys())
            }
        
        # 2. โหลด template ที่ตรงกัน
        template = self.templates.get(detected_intent)
        if not template:
            return {
                "status": "error",
                "message": f"ไม่พบ template สำหรับ {detected_intent}"
            }
        
        # 3. จัดการ session state
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "template": detected_intent,
                "current_step": 0,
                "answers": {},
                "context": {}
            }
        
        session = self.active_sessions[session_id]
        
        # ถ้าเป็น intent ใหม่ รีเซ็ต session
        if session["template"] != detected_intent:
            session = {
                "template": detected_intent,
                "current_step": 0,
                "answers": {},
                "context": {}
            }
            self.active_sessions[session_id] = session
        
        # 4. ประมวลผลคำตอบ (ถ้ามี)
        if session["current_step"] > 0:
            current_question = template["questions"][session["current_step"] - 1]
            session["answers"][current_question["id"]] = user_input
            
            # อัพเดท context ตามคำตอบ
            if "update_context" in current_question:
                for key, value in current_question["update_context"].items():
                    session["context"][key] = value
        
        # 5. ตรวจสอบว่าเสร็จสิ้นหรือยัง
        if session["current_step"] >= len(template["questions"]):
            # สร้างสรุปผล
            summary = self._generate_summary(template, session)
            # รีเซ็ต session
            del self.active_sessions[session_id]
            return {
                "status": "completed",
                "template": detected_intent,
                "summary": summary,
                "message": "เยี่ยมเลยครับ! นี่คือแผนงานที่คุณสามารถนำไปใช้ได้:"
            }
        
        # 6. ได้คำถามถัดไป
        current_question = template["questions"][session["current_step"]]
        session["current_step"] += 1
        
        # เพิ่มคำแนะนำ/ตัวเลือก
        question_text = current_question["question"]
        if "options" in current_question:
            options_text = "\n\nตัวเลือกแนะนำ:\n"
            for i, opt in enumerate(current_question["options"], 1):
                options_text += f"{i}. {opt['label']} - {opt.get('description', '')}\n"
            question_text += options_text
        
        if "tips" in current_question:
            question_text += f"\n💡 เคล็ดลับ: {current_question['tips']}"
        
        return {
            "status": "in_progress",
            "template": detected_intent,
            "step": session["current_step"],
            "total_steps": len(template["questions"]),
            "next_question": question_text,
            "question_id": current_question["id"],
            "options": current_question.get("options", []),
            "progress": f"{session['current_step']}/{len(template['questions'])}"
        }
    
    def _generate_summary(self, template: Dict, session: Dict) -> str:
        """สร้างสรุปผลจากคำตอบทั้งหมด"""
        summary_parts = [f"# แผนงาน: {template.get('name', 'Project')}"]
        summary_parts.append(f"\n**ประเภท:** {template.get('description', '')}\n")
        
        for q in template["questions"]:
            answer = session["answers"].get(q["id"], "ไม่ได้ระบุ")
            summary_parts.append(f"- **{q['question']}**: {answer}")
        
        if "final_recommendations" in template:
            summary_parts.append("\n## คำแนะนำเพิ่มเติม")
            for rec in template["final_recommendations"]:
                summary_parts.append(f"- {rec}")
        
        return "\n".join(summary_parts)
    
    def reset_session(self, session_id: str = "default"):
        """รีเซ็ต session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        return {"status": "reset", "message": "เริ่มการสนทนาใหม่แล้ว"}


# ฟังก์ชัน helper สำหรับใช้งานง่าย
def create_flow_engine(templates_dir: str = "templates") -> StateFlowEngine:
    return StateFlowEngine(templates_dir)
