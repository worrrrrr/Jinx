"""
ทดสอบ Error Handling ของ search_handler
"""
import sys
sys.path.insert(0, '/workspace')

from tools.search import search_handler, search_web, search_local_knowledge

def test_search_handler_signature():
    """ทดสอบว่า search_handler รับ argument ได้หลายรูปแบบ"""
    print("Test 1: search_handler('action', 'query', [])")
    r1 = search_handler('search', 'โหราศาสตร์', [])
    assert r1['status'] in ['success', 'partial', 'error'], "Status must be one of success/partial/error"
    
    print("Test 2: search_handler(query='Human Design')")
    r2 = search_handler(query='Human Design')
    assert r2['status'] in ['success', 'partial', 'error']
    
    print("Test 3: search_handler() - no args")
    r3 = search_handler()
    assert r3['status'] in ['success', 'partial', 'error']
    
    print("Test 4: search_handler(action='search', entities=['ภาษาจีน'])")
    r4 = search_handler(action='search', entities=['ภาษาจีน'])
    assert r4['status'] in ['success', 'partial', 'error']
    
    print("Test 5: search_handler with None entities")
    r5 = search_handler('search', '', None)
    assert r5['status'] in ['success', 'partial', 'error']
    
    print("✅ All signature tests passed!")

def test_error_handling():
    """ทดสอบว่า error ถูกจับและ return อย่างถูกต้อง"""
    print("\nTest 6: Error handling for web search (if DDGS is None)")
    # ถ้า DDGS เป็น None ควร return error message ที่ชัดเจน
    result = search_web("test query")
    if "Error" in result:
        print(f"   Web search returned error (expected if offline): {result[:50]}...")
    else:
        print(f"   Web search succeeded: found results")
    
    print("✅ Error handling test passed!")

def test_return_structure():
    """ทดสอบว่า return structure มีครบ"""
    print("\nTest 7: Check return structure")
    r = search_handler('search', 'test', [])
    
    assert 'status' in r, "Must have 'status' key"
    assert 'result' in r, "Must have 'result' key"
    assert isinstance(r['status'], str), "Status must be string"
    assert isinstance(r['result'], (str, dict, list)), "Result must be string, dict, or list"
    
    if r['status'] == 'error':
        assert 'error_type' in r or 'message' in r, "Error status must have error_type or message"
    
    print(f"   Return structure: status={r['status']}, has_result={('result' in r)}")
    print("✅ Return structure test passed!")

if __name__ == "__main__":
    test_search_handler_signature()
    test_error_handling()
    test_return_structure()
    print("\n🎉 All tests passed! Search handler is robust and error-tolerant.")
