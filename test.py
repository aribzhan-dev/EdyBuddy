import requests

TOKEN = "8367275884:AAFNUhPDM3Gmq7dASV2mRnxfrvD6egler-g"

try:
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=5)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)
except Exception as e:
    print("ERROR:", e)