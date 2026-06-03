import os
import json
import sys
from ollama import Client

# 1. Configuration
CLIENT = Client()
MODEL = 'gpt-oss:120b-cloud'
OUTPUT_DIR = "tools"

def save_to_file(filename, content):
    """ทำความสะอาดโค้ดและเขียนลงไฟล์"""
    # ล้าง Markdown ที่มักติดมากับ LLM
    clean_content = content.replace("```python", "").replace("```", "").strip()
    
    # ตรวจสอบ path เพื่อความปลอดภัย
    filepath = os.path.join(os.getcwd(), filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    return f"✅ ไฟล์ {filename} ถูกสร้างเรียบร้อยแล้ว!"

def main():
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("สั่งงาน Jinx: ")

    # 2. บังคับ Format ให้ AI
    system_instruction = (
        "คุณคือ Jinx, AI Engineering Partner. "
        "หากผู้ใช้สั่งให้สร้างไฟล์ ให้ตอบเป็น JSON เท่านั้น: "
        '{"filename": "tools/your_file.py", "content": "source code"}. '
        "ถ้าไม่ใช่การสร้างไฟล์ ให้ตอบข้อความปกติแบบกระชับ"
    )

    response = CLIENT.chat(model=MODEL, messages=[
        {'role': 'system', 'content': system_instruction},
        {'role': 'user', 'content': user_prompt}
    ])

    text = response['message']['content'].strip()

    # 3. แยก logic การประมวลผล
    try:
        if text.startswith("{") and text.endswith("}"):
            data = json.loads(text)
            print(save_to_file(data['filename'], data['content']))
        else:
            print(f"\nJinx: {text}")
    except json.JSONDecodeError:
        print(f"\nJinx: {text}")

if __name__ == "__main__":
    main()