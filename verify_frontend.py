import sys
import os
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
    assert "Mike — Your Insurance Navigator" in html_content
    assert "id=\"app-bg\"" in html_content
    assert "id=\"spotlight-overlay\"" in html_content
    assert "id=\"landing-container\"" in html_content
    assert "id=\"onboarding-controls\"" in html_content
    assert "id=\"onboarding-progress-tracker\"" in html_content
    assert "app.js" in html_content
    print("Static page serving validation passed!")

    # 2. Test style.css fetching
    print("Testing GET /style.css ...")
    res_css = client.get("/style.css")
    print("Status Code:", res_css.status_code)
    assert res_css.status_code == 200
    assert "animated-gradient" in res_css.text
    assert "--teal-accent" in res_css.text
    print("CSS serving validation passed!")

    # 3. Test app.js fetching
    print("Testing GET /app.js ...")
    res_js = client.get("/app.js")
    print("Status Code:", res_js.status_code)
    assert res_js.status_code == 200
    assert "onboardingNext" in res_js.text
    assert "adjustInputDock" in res_js.text
    assert "drawHanddrawnCircleAndArrow" in res_js.text
    print("Javascript serving validation passed!")

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
