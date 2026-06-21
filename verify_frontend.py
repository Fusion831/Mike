import sys
import os
import re
from fastapi.testclient import TestClient
from main import app

# Ensure workspace root in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_frontend_serving():
    print("Initializing FastAPI TestClient...")
    client = TestClient(app)
    
    # 1. Test Root Route (HTML Ingestion)
    print("Testing GET / ...")
    res = client.get("/")
    print("Status Code:", res.status_code)
    assert res.status_code == 200
    
    html_content = res.text
    print("Checking HTML structure tokens...")
    assert "Mike — Your Health Insurance Guide" in html_content
    assert "animated-gradient" in html_content
    
    # Extract CSS stylesheet link from Next.js output
    css_match = re.search(r'href="(/_next/static/chunks/[^"]+\.css)"', html_content)
    if css_match:
        css_path = css_match.group(1)
        print(f"Testing GET {css_path} ...")
        res_css = client.get(css_path)
        print("Status Code:", res_css.status_code)
        assert res_css.status_code == 200
        assert "animated-gradient" in res_css.text or "background" in res_css.text
        print("CSS serving validation passed!")
    else:
        print("Warning: CSS file link not found in index.html, skipping CSS contents check.")
        
    # Extract JS script link from Next.js output
    js_match = re.search(r'src="(/_next/static/chunks/[^"]+\.js)"', html_content)
    if js_match:
        js_path = js_match.group(1)
        print(f"Testing GET {js_path} ...")
        res_js = client.get(js_path)
        print("Status Code:", res_js.status_code)
        assert res_js.status_code == 200
        print("Javascript serving validation passed!")
    else:
        print("Warning: JS file link not found in index.html, skipping JS serving check.")

if __name__ == "__main__":
    try:
        test_frontend_serving()
        print("\n=== UPDATED FRONTEND SERVING TESTS PASSED SUCCESSFULLY ===")
        sys.exit(0)
    except Exception as e:
        print("\n=== UPDATED FRONTEND SERVING TESTS FAILED ===")
        import traceback
        traceback.print_exc()
        sys.exit(1)
