"""Knowledge search: normalization, fuzzy, aliases."""

from tools.search import (
    normalize_qa_query,
    build_search_query,
    expand_search_terms,
    search_local_knowledge,
    reset_alias_cache,
    _load_aliases,
)


def test_normalize_qa_thai():
    assert normalize_qa_query("Python คืออะไร") == "Python"


def test_build_search_query_from_topic():
    assert build_search_query("ช่วยอธิบาย intent", []) == "intent"


def test_build_search_query_strips_search_verb():
    assert build_search_query("ค้นหา intent", []) == "intent"


def test_aliases_loaded_from_common():
    reset_alias_cache()
    aliases = _load_aliases()
    assert "python" in aliases or any("python" in v for v in aliases.values())


def test_expand_terms_typo_pythonn():
    reset_alias_cache()
    terms = expand_search_terms("pythonn")
    assert any("python" in t.lower() for t in terms)


def test_fuzzy_search_finds_python_with_typo():
    reset_alias_cache()
    out = search_local_knowledge("search", "pythonn", [])
    assert out["status"] == "success"
    assert out["engine"] == "fuzzy_ranked"
    result = out["result"]
    assert isinstance(result, list)
    sources = " ".join(h["source"] for h in result).lower()
    assert "python" in sources


def test_search_jinx_overview_in_common():
    reset_alias_cache()
    out = search_local_knowledge("answer_question", "Jinx คืออะไร", [])
    assert out["status"] == "success"
    text = str(out["result"]).lower()
    assert "common" in text or "runtime" in text or "perception" in text


def test_search_returns_score():
    out = search_local_knowledge("search", "intent", [])
    if isinstance(out.get("result"), list) and out["result"]:
        assert "score" in out["result"][0]
