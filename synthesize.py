#!/usr/bin/env python3
import sys
import requests

webhookurl = "http://homeassistant.local:8123/api/webhook/"
text = sys.stdin.read().strip()
print(f"Text to speech text: {text} to {webhookurl}")

json_payload = { "response": text }
print(f"Payload: {json_payload}")

response = requests.post(
    webhookurl,
    json=json_payload,
    headers={"Content-Type": "application/json"},
    verify=False
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")