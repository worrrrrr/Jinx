import os
import gradio as gr
import logging
from core.orchestrator import Orchestrator

# ตั้งค่า Logging ให้เห็นในหน้า Console ของ Hugging Face
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JinxGradio")

# โหลดสมอง Jinx
try:
    jinx = Orchestrator()
    logger.info("✅ Orchestrator loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load Orchestrator: {e}")
    jinx = None

def chat_interface(message, history):
    """ฟังก์ชันหลักที่เชื่อมหน้าจอเข้ากับสมอง Jinx"""
    if jinx is None:
        return "⚠️ ระบบ Orchestrator ไม่พร้อมใช้งาน กรุณาตรวจสอบ Log"
    try:
        # เรียกใช้ jinx.run() ตามโครงสร้างที่คุณเขียนใน core/orchestrator.py
        response = jinx.run(message)
        return response
    except Exception as e:
        logger.error(f"Error during run: {e}")
        return f"เกิดข้อผิดพลาด: {str(e)}"

# สร้างหน้าจอ UI ด้วย Gradio (ตัวนี้จะสร้างหน้า Chat และปุ่ม View API ให้โดยอัตโนมัติ)
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ✨ JINX AGENT")
    gr.Markdown("Cognitive Architecture - ระบบวิเคราะห์สังเคราะห์และโหราศาสตร์")
    
    chat_box = gr.ChatInterface(
        fn=chat_interface,
        title=None, # ใส่ใน Markdown ด้านบนแทน
        retry_btn="ลองใหม่",
        undo_btn="ย้อนกลับ",
        clear_btn="ล้างแชท"
    )

if __name__ == "__main__":
    # Hugging Face บังคับพอร์ต 7860
    port = int(os.environ.get("PORT", 7860))
    logger.info(f"🚀 Starting Gradio on port {port}")
    
    # รันหน้าจอ UI
    demo.launch(server_name="0.0.0.0", server_port=port)