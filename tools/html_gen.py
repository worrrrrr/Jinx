# tools/html_gen.py — HTML Generator

import re
from typing import Dict, Any, List, Callable


def get_tools() -> Dict[str, Callable]:
    return {
        "generate_html": generate_html_handler,
        "html": generate_html_handler,
    }


TEMPLATES = {
    "simple": """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }}
h1 {{ color: #333; }}
</style>
</head>
<body>
<h1>{title}</h1>
{content}
</body>
</html>""",

    "card": """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
body {{ font-family: system-ui, sans-serif; background: #f5f5f5; margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
.card {{ background: white; border-radius: 16px; padding: 2rem; margin: 2rem; max-width: 600px; box-shadow: 0 4px 24px rgba(0,0,0,0.1); }}
h1 {{ margin-top: 0; color: #222; }}
</style>
</head>
<body>
<div class="card">
<h1>{title}</h1>
{content}
</div>
</body>
</html>""",
}


def generate_html_handler(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    if not inp and not entities:
        return {"status": "fail", "message": "ไม่พบเนื้อหาที่จะสร้าง HTML"}

    text = inp or " ".join(entities)
    title = _extract_title(text)
    template_name = _detect_template(text)
    content = _convert_to_html(text, title)

    template = TEMPLATES.get(template_name, TEMPLATES["simple"])
    html = template.format(title=title, content=content)

    return {
        "status": "success",
        "result": html,
        "title": title,
        "template": template_name,
    }


def _extract_title(text: str) -> str:
    # มองหา "ชื่อเรื่อง ..." หรือขึ้นบรรทัดแรกที่ไม่มีคำสั่ง
    m = re.search(r"(?:ชื่อเรื่อง|หัวข้อ|title)\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # ใช้บรรทัดแรกที่ไม่ใช่คำสั่ง
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines:
        if not re.match(r"(สร้าง|ทำ|generate|html|card)", line, re.IGNORECASE):
            return line[:60]
    return "หน้าเว็บ"


def _detect_template(text: str) -> str:
    if "การ์ด" in text or "card" in text.lower():
        return "card"
    return "simple"


def _convert_to_html(text: str, title: str) -> str:
    # ตัดคำสั่งออก
    clean = re.sub(r"(?:สร้าง|ทำ|generate|html|card|ชื่อเรื่อง|หัวข้อ|title)\s*", "", text, flags=re.IGNORECASE)
    clean = clean.replace(title, "", 1).strip()

    lines = clean.split("\n")
    html_parts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("- ") or line.startswith("* "):
            html_parts.append(f"<li>{line[2:]}</li>")
        elif line.startswith("## "):
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_parts.append(f"<h2>{line[2:]}</h2>")
        else:
            html_parts.append(f"<p>{line}</p>")

    if any("<li>" in p for p in html_parts):
        list_items = [p for p in html_parts if "<li>" in p]
        others = [p for p in html_parts if "<li>" not in p]
        result = "\n".join(others)
        if list_items:
            result += "\n<ul>\n" + "\n".join(list_items) + "\n</ul>"
        return result
    return "\n".join(html_parts)
