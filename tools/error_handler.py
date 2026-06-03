import traceback
import logging

class ErrorHandler:
    def __init__(self):
        # รวบรวม Rule-based patterns ที่พบบ่อย
        self.rules = {
            "MISSING_LIBRARY": ["module", "not found", "no module named"],
            "SYNTAX_ERROR": ["syntaxerror", "invalid syntax"],
            "UNDEFINED_VARIABLE": ["nameerror", "is not defined"],
            "TYPE_ERROR": ["typeerror", "not callable", "must be str"]
        }

    def classify_error(self, error_obj):
        """วิเคราะห์ประเภท Error เบื้องต้นโดยไม่ใช้ LLM"""
        err_msg = str(error_obj).lower()
        
        for err_type, patterns in self.rules.items():
            if any(p in err_msg for p in patterns):
                return err_type
        return "UNKNOWN_ERROR"

    def get_remediation(self, error_type, code):
        """คืนค่าวิธีแก้ปัญหาเบื้องต้น หรือเตรียมข้อมูลส่งให้ LLM"""
        if error_type == "MISSING_LIBRARY":
            return "CHECK_IMPORTS"
        elif error_type == "UNDEFINED_VARIABLE":
            return "CHECK_VARIABLE_SCOPE"
        
        # กรณีที่ไม่รู้ ต้องส่งให้ LLM วิเคราะห์ผ่าน Traceback
        return "LLM_ANALYSIS_REQUIRED"

    def handle(self, error_obj, code):
        """ฟังก์ชันหลักสำหรับเรียกใช้งานใน Loop"""
        error_type = self.classify_error(error_obj)
        remediation = self.get_remediation(error_type, code)
        
        return {
            "error_type": error_type,
            "remediation": remediation,
            "traceback": traceback.format_exc()
        }

# ตัวอย่างการใช้งานเบื้องต้น
if __name__ == "__main__":
    handler = ErrorHandler()
    try:
        # สมมติโค้ดที่รันแล้วพัง
        import non_existent_library
    except Exception as e:
        report = handler.handle(e, "import non_existent_library")
        print(f"Detected: {report['error_type']} -> {report['remediation']}")