# tools/search.py — Knowledge Vault search (fuzzy + ranking)

import os
import re
from dataclasses import dataclass
from typing import Dict, Any, List, Callable, Optional, Set, Tuple

from rapidfuzz import fuzz

DEFAULT_KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge"
)

ALIAS_CACHE: Optional[Dict[str, List[str]]] = None
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
ALIAS_TABLE_ROW_RE = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE
)


@dataclass(order=True)
class SearchHit:
  score: float
  title: str = ""
  snippet: str = ""
  source: str = ""
  line_number: int = 0
  match_kind: str = ""


def get_tools() -> Dict[str, Callable]:
    return {
        "web_search": search_local_knowledge,
        "search": search_local_knowledge,
        "answer_question": search_local_knowledge,
        "search_knowledge": search_local_knowledge,
    }


# tools/search.py

import os
import re
from typing import Dict, Any, List

def search_local_knowledge(action: str, inp: str, entities: List[str] = None) -> Dict[str, Any]:
    """
    ค้นหาเนื้อหาที่เกี่ยวข้องจากเอกสารในโฟลเดอร์ data/knowledge
    """
    knowledge_dir = os.path.join("data", "knowledge")
    query = inp.strip() if inp else ""
    
    # ดึงคีย์เวิร์ดสำคัญจากเอนทิตีหรือข้อความเพื่อช่วยในการสืบค้นหลัก
    keywords = set(entities) if entities else set()
    if query:
        keywords.update(re.findall(r"\b\w+\b", query.lower()))
    
    if not os.path.exists(knowledge_dir):
        # สร้างโฟลเดอร์ออโต้หากระบบยังไม่มี เพื่อพร้อมรับการวางไฟล์ข้อมูล
        os.makedirs(knowledge_dir, exist_ok=True)
        return {
            "status": "success",
            "result": [],
            "message": f"สร้างโฟลเดอร์ {knowledge_dir} ใหม่เรียบร้อยแล้ว โปรดนำไฟล์ .md หรือ .txt มาใส่เพิ่มความรู้"
        }

    matched_hits = []
    
    # วนลูปอ่านไฟล์ข้อมูลใน data/knowledge (รองรับไฟล์ข้อความดิบ .txt และ .md)
    for root, _, files in os.walk(knowledge_dir):
        for file in files:
            if file.endswith((".md", ".txt")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                        # แบ่งเนื้อหาออกเป็นย่อหน้าย่อย ๆ เพื่อประหยัดพื้นที่ Token และดึงข้อมูลได้เจาะจง
                        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                        
                        for idx, para in enumerate(paragraphs):
                            # ตรวจหาจุดแมตช์เชิงคำค้นหาหรือเอนทิตีที่เกี่ยวข้อง
                            para_lower = para.lower()
                            match_score = sum(1 for kw in keywords if kw in para_lower)
                            
                            if match_score > 0:
                                snippet_clean = re.sub(r"\s+", " ", para)
                                matched_hits.append({
                                    "title": file,
                                    "source": f"{file}#p{idx+1}",
                                    "snippet": snippet_clean,
                                    "score": match_score
                                })
                except Exception:
                    continue

    # เรียงลำดับย่อหน้าที่มีคะแนนความสอดคล้องกับหัวข้อคำถามสูงสุด
    matched_hits.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "status": "success",
        "result": matched_hits[:3], # ส่งกลับย่อยอดพารากราฟที่ดีที่สุด 3 ลำดับแรก
        "query": query
    }

def _resolve_kb_dir() -> Optional[str]:
    if os.path.exists(DEFAULT_KNOWLEDGE_DIR):
        return DEFAULT_KNOWLEDGE_DIR
    fallback = os.path.join("data", "knowledge")
    return fallback if os.path.exists(fallback) else None


def _search_vault(kb_dir: str, terms: List[str], raw_query: str) -> List[SearchHit]:
    all_hits: List[SearchHit] = []
    for root, _, files in os.walk(kb_dir):
        if ".obsidian" in root.replace("\\", "/"):
            continue
        for name in files:
            if not name.endswith((".md", ".txt", ".json")):
                continue
            path = os.path.join(root, name)
            all_hits.extend(_score_file(path, terms, raw_query))
    all_hits.sort(reverse=True)
    return _dedupe_hits(all_hits)[:8]


def _score_file(file_path: str, terms: List[str], raw_query: str) -> List[SearchHit]:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.splitlines()
    except OSError:
        return []

    rel = os.path.relpath(file_path)
    basename = os.path.basename(file_path)
    hits: List[SearchHit] = []

    file_score = _best_term_score(basename, terms, raw_query)
    if file_score >= 55:
        hits.append(
            SearchHit(
                score=file_score + 15,
                title=basename,
                snippet=_first_meaningful_line(lines) or basename,
                source=rel,
                line_number=1,
                match_kind="filename",
            )
        )

    for m in HEADING_RE.finditer(content):
        heading = m.group(1).strip()
        h_score = _best_term_score(heading, terms, raw_query)
        if h_score >= 50:
            line_no = content[: m.start()].count("\n") + 1
            hits.append(
                SearchHit(
                    score=h_score + 10,
                    title=basename,
                    snippet=f"## {heading}",
                    source=rel,
                    line_number=line_no,
                    match_kind="heading",
                )
            )

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("```"):
            continue
        line_score = _best_term_score(stripped, terms, raw_query)
        if line_score < 45:
            continue
        start = max(0, idx - 1)
        end = min(len(lines), idx + 2)
        snippet_lines = [l.strip() for l in lines[start:end] if l.strip()]
        hits.append(
            SearchHit(
                score=line_score,
                title=basename,
                snippet=" ... ".join(snippet_lines)[:280],
                source=rel,
                line_number=idx + 1,
                match_kind="content",
            )
        )

    return hits


def _best_term_score(text: str, terms: List[str], raw_query: str) -> float:
    if not text:
        return 0.0
    lower = text.lower()
    best = 0.0
    for term in terms:
        t = term.lower()
        if t in lower:
            best = max(best, 95.0)
            continue
        best = max(best, float(fuzz.partial_ratio(t, lower)))
    best = max(best, float(fuzz.partial_ratio(raw_query.lower(), lower)))
    return best


def _dedupe_hits(hits: List[SearchHit]) -> List[SearchHit]:
    seen: Set[Tuple[str, int]] = set()
    out: List[SearchHit] = []
    for h in hits:
        key = (h.source, h.line_number)
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out


def _first_meaningful_line(lines: List[str]) -> str:
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("---"):
            return s[:200]
    return ""


def expand_search_terms(query: str) -> List[str]:
    """คำค้นหาหลัก + คำจาก alias table ใน common.md."""
    terms: List[str] = []
    q = query.strip()
    if q:
        terms.append(q)
    for part in re.split(r"[\s,]+", q):
        if len(part) >= 2 and part not in terms:
            terms.append(part)

    aliases = _load_aliases()
    q_lower = q.lower()
    for key, targets in aliases.items():
        matched = key in q_lower or (
            len(key) >= 3 and fuzz.partial_ratio(key, q_lower) >= 82
        )
        if matched:
            for target in targets:
                if target not in terms:
                    terms.append(target)

    return terms[:12]


def _load_aliases() -> Dict[str, List[str]]:
    global ALIAS_CACHE
    if ALIAS_CACHE is not None:
        return ALIAS_CACHE

    ALIAS_CACHE = {}
    common_path = os.path.join(DEFAULT_KNOWLEDGE_DIR, "common.md")
    if not os.path.isfile(common_path):
        return ALIAS_CACHE

    try:
        with open(common_path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return ALIAS_CACHE

    in_alias_section = False
    for line in text.splitlines():
        if re.search(r"##\s+.*[Aa]lias|คำพ้อง", line):
            in_alias_section = True
            continue
        if in_alias_section and line.startswith("## ") and "alias" not in line.lower():
            in_alias_section = False
        if not in_alias_section:
            continue
        m = ALIAS_TABLE_ROW_RE.match(line)
        if not m or m.group(1).strip().startswith("---"):
            continue
        left, right = m.group(1).strip(), m.group(2).strip()
        if left.lower() in ("ผู้ใช้อาจพูด", "user says"):
            continue
        targets: List[str] = []
        for ref in re.findall(r"([\w\-]+\.md)", right, re.IGNORECASE):
            targets.append(ref.replace(".md", ""))
        for ref in re.findall(r"\[\[([\w\-]+)\.md\]\]", right):
            targets.append(ref)
        if "common" in right.lower() and "common" not in targets:
            targets.append("common")
        for part in re.split(r"[,，、]", left):
            key = part.strip().lower()
            if len(key) >= 2:
                ALIAS_CACHE.setdefault(key, [])
                for t in targets:
                    if t and t not in ALIAS_CACHE[key]:
                        ALIAS_CACHE[key].append(t)
                if not targets and "common" in right.lower():
                    if "common" not in ALIAS_CACHE[key]:
                        ALIAS_CACHE[key].append("common")

    return ALIAS_CACHE


def build_search_query(inp: str, entities: List[str]) -> str:
    query = inp.strip() if inp else ""
    if not query and entities:
        query = " ".join(str(e).strip() for e in entities if str(e).strip())
    if not query:
        return ""
    return normalize_qa_query(query)


def normalize_qa_query(text: str) -> str:
    q = re.sub(r"\s+", " ", text).strip()
    if not q:
        return ""

    leading = [
        r"^(?:ช่วย)?(?:อธิบาย|บอก|เล่า)(?:ให้)?(?:ฉัน|ผม|หน่อย)?(?:เกี่ยวกับ|เรื่อง)?\s*",
        r"^(?:please\s+)?(?:explain|tell\s+me\s+about|describe)\s+",
        r"^(?:what\s+is|what\s+are|what's)\s+",
        r"^(?:how\s+(?:do|to|can)\s+(?:i|we)\s+)",
        r"^(?:ค้นหา|หา|search|find)\s+",
    ]
    trailing = [
        r"\s*(?:คือ|หมายถึง)\s*(?:อะไร|ยังไง)?\s*$",
        r"\s*คืออะไร\s*$",
        r"\s*(?:หมายความว่า|แปลว่า)\s*(?:อะไร)?\s*$",
        r"\s*(?:ทำไม|เพราะอะไร)\s*$",
        r"\s*(?:อย่างไร|ยังไง|วิธี)\s*$",
        r"\s*\?\s*$",
        r"\s*(?:what|why|how|who|when|where)\s*\??\s*$",
    ]

    for pat in leading:
        q = re.sub(pat, "", q, flags=re.IGNORECASE)
    for pat in trailing:
        q = re.sub(pat, "", q, flags=re.IGNORECASE)

    q = q.strip(" '\".,!?")
    if q:
        return q

    tokens = [t for t in re.split(r"\s+", text) if len(t) >= 2]
    return tokens[0] if tokens else text.strip()


def reset_alias_cache() -> None:
    """สำหรับเทส — โหลด alias จาก common.md ใหม่."""
    global ALIAS_CACHE
    ALIAS_CACHE = None
