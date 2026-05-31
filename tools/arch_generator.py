import os

class AgentProduction:
    def __init__(self):
        # ข้อมูลตายตัวที่ห้ามเปลี่ยน
        self.project_name = "AI_CORE_SYSTEM"
        self.registry = {"planner": "core.plan", "executor": "core.run", "validator": "core.check"}
        
        if not os.path.exists('docs'): os.makedirs('docs')

    def generate_project(self):
        # โครงสร้างที่ถูกล็อคไว้
        structure = {
            "README.md": f"# {self.project_name}\n\nระบบขับเคลื่อนด้วย Orchestrator และ Registry ที่เข้มงวด",
            "RULES.md": f"1. ห้ามแก้ไขชื่อฟังก์ชันที่มีใน Registry: {list(self.registry.keys())}\n2. ต้องรันผ่าน Orchestrator เท่านั้น",
            "ARCHITECTURE.md": "# โครงสร้างระบบ\n- Planner: เรียกใช้ผ่าน {planner}\n- Executor: เรียกใช้ผ่าน {executor}"
        }

        for file, content in structure.items():
            with open(f"docs/{file}", "w") as f:
                f.write(content.format(**self.registry))
        
        return "--- ระบบสร้างโครงสร้างมาตรฐานเสร็จสิ้น ---"

if __name__ == "__main__":
    print(AgentProduction().generate_project())