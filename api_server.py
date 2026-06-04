import os
import logging
import gradio as gr
from core.orchestrator import Orchestrator

# 1. ตั้งค่า Logging เพื่อให้คุณดูสถานะบน Hugging Face Console ได้ชัดเจน
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("JinxProduction")

# 2. เริ่มต้นระบบสมอง Jinx (Global Instance)
# เราโหลดไว้ข้างนอกฟังก์ชันเพื่อให้โหลดเพียงครั้งเดียวตอนเริ่ม Server
try:
    logger.info("กำลังเริ่มต้นระบบ Jinx Orchestrator...")
    jinx = Orchestrator()
    logger.info("✅ ระบบ Jinx Orchestrator พร้อมทำงานแล้ว")
except Exception as e:
    logger.error(f"❌ ไม่สามารถเริ่มระบบได้เนื่องจาก: {str(e)}", exc_info=True)
    jinx = None

def jinx_chat_engine(message, history):
    """
    ฟังก์ชันหลักที่เชื่อมต่อหน้าจอ UI กับตรรกะการประมวลผล
    message: ข้อความที่ผู้ใช้พิมพ์ส่งมา
    history: ประวัติการสนทนา (Gradio จะจัดการให้โดยอัตโนมัติ)
    """
    # ตรวจสอบว่าระบบสมองโหลดสำเร็จหรือไม่
    if jinx is None:
        return "⚠️ ขณะนี้ระบบสมอง (Orchestrator) ขัดข้อง กรุณาตรวจสอบ logs ของ Container"
    
    # ตรวจสอบข้อความว่างเปล่า
    if not message.strip():
        return "กรุณาพิมพ์ข้อความเพื่อเริ่มต้นการสนทนาครับ"

    try:
        logger.info(f"ได้รับข้อความ: {message}")
        # เรียกใช้งาน .run() จาก core/orchestrator.py ของคุณ
        # ซึ่งจะไปเรียก Perception, Execution และ Tools ต่อไป
        response = jinx.run(message)
        logger.info("ส่งคำตอบกลับสำเร็จ")
        return response
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดระหว่างประมวลผล: {str(e)}", exc_info=True)
        return f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"

# 3. สร้างส่วนแสดงผล (Gradio Interface)
# เราใช้ gr.Blocks เพื่อความยืดหยุ่นในการปรับแต่งหน้าตาในอนาคต
with gr.Blocks(theme=gr.themes.Soft(), title="JINX AGENT v1.0") as demo:
    gr.Markdown("""
    # 🧠 JINX AGENT: Cognitive Architecture
    ระบบวิเคราะห์อัตลักษณ์สังเคราะห์และโหราศาสตร์ประยุกต์ (Production Mode)
    """)
    
    # หน้าจอแชทหลัก
    chat_interface = gr.ChatInterface(
        fn=jinx_chat_engine,
        chatbot=gr.Chatbot(height=500, show_copy_button=True),
        textbox=gr.Textbox(
            placeholder="พิมพ์คำสั่งหรือข้อความที่นี่ (เช่น /astro 20/08/1992 16:49)", 
            container=False, 
            scale=7
        ),
        submit_btn="ส่งข้อความ",
        retry_btn="ลองใหม่",
        undo_btn="ลบข้อความล่าสุด",
        clear_btn="ล้างการสนทนา",
    )
    
    gr.Markdown("""
    ---
    **คำแนะนำการใช้งาน:**
    * ใช้คำสั่ง `/astro` ตามด้วยวันเวลาเกิดเพื่อวิเคราะห์ดวง
    * ระบบนี้เชื่อมต่อกับ **Groq (Llama 3.3)** เป็นสมองหลัก
    * หากต้องการใช้งานผ่าน API สามารถกดที่ปุ่ม **"view api"** ด้านล่างสุดได้
    """)

# 4. ส่วนการรัน Server
if __name__ == "__main__":
    # Hugging Face Spaces จะส่ง Port มาให้ทาง Environment Variable ชื่อ PORT (ปกติคือ 7860)
    server_port = int(os.environ.get("PORT", 7860))
    
    logger.info(f"กำลังเปิดใช้งาน Server บนพอร์ต {server_port}...")
    
    # สั่ง Launch โดยเปิดโหมด API ไว้เพื่อให้แสดงปุ่ม View API
    demo.launch(
        server_name="0.0.0.0",
        server_port=server_port,
        show_api=True,      # บังคับให้แสดงเมนู API
        share=False         # บน Hugging Face ไม่ต้องเปิด share=True
    )