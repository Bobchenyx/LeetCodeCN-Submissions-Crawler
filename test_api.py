import requests
import json

LEETCODE_SESSION = ""
CSRF_TOKEN = ""

session = requests.session()
session.cookies.set('LEETCODE_SESSION', LEETCODE_SESSION)
session.cookies.set('csrftoken', CSRF_TOKEN)

headers = {
    'X-CSRFToken': CSRF_TOKEN,
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json'
}

url = "https://leetcode.cn/api/submissions/?offset=0&limit=1"
response = session.get(url, headers=headers)

print(f"Status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"Keys in response: {list(data.keys())}")
    print(f"Response structure: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
