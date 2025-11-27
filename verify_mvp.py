import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    try:
        r = requests.get("http://localhost:8000/")
        assert r.status_code == 200
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)

def main():
    print("Running MVP Verification...")
    test_health()
    # Add more tests here if server is running
    print("MVP Verification Complete.")

if __name__ == "__main__":
    main()
