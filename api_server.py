import os
import gradio as gr
import logging
from core.orchestrator import Orchestrator

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JinxStable")

# โหลด Orchestrator เพียงครั้งเดียว (Global Instance)
try:
    jinx = Orchestrator()
    logger.info("✅ Jinx Orchestrator is ready")
except Exception as e:
    logger.error(f"❌ Initialization Error: {e}")
    jinx = None

def respond(message, history):
    """
    ฟังก์ชันตอบโต้ที่รักษาเสถียรภาพของ UI
    message: ข้อความที่ผู้ใช้พิมพ์
    history: ประวัติการคุย (Gradio จัดการให้)
    """
    if jinx is None:
        return "⚠️ ระบบไม่พร้อมใช้งาน (Orchestrator Load Error)"
    
    try:
        # เรียกใช้ jinx.run() โดยตรง
        # หาก jinx.run() มีการจัดการ memory ภายในอยู่แล้ว ไม่ต้องส่ง history เข้าไป
        bot_message = jinx.run(message)
        return bot_message
    except Exception as e:
        logger.error(f"Processing Error: {e}")
        return f"เกิดข้อผิดพลาด: {str(e)}"

# ใช้ Blocks เพื่อคุมพฤติกรรมหน้าจอให้เสถียรที่สุด
with gr.Blocks(theme=gr.themes.Soft(), title="JINX AGENT") as demo:
    gr.Markdown("# ✨ JINX AGENT")
    
    # การใช้ ChatInterface ภายใน Blocks จะช่วยให้ Focus ของ Input มั่นคงขึ้น
    chat_ui = gr.ChatInterface(
        fn=respond,
        textbox=gr.Textbox(placeholder="พิมพ์ข้อความที่นี่...", container=False, scale=7),
        submit_btn="ส่ง",
        stop_btn="หยุด",
        retry_btn="ลองใหม่",
        undo_btn="ย้อนกลับ",
        clear_btn="ล้างแชท",
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    # ตั้งค่าตัวเลือกการโชว์ผลลัพธ์ให้ลื่นไหล (Show API จะมาเองอัตโนมัติ)
    demo.launch(
        server_name="0.0.0.0", 
        server_port=port,
        share=False,
        show_api=True  # ยืนยันว่าเปิด API View แน่นอน
    )