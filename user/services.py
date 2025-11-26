import json
import requests
import secrets
import string

def generate_password(length=6):
    allowed_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_"
    return ''.join(secrets.choice(allowed_chars) for _ in range(length))

def send_tg_mgs(to_id,message):
    Headers = { 'Content-Type':'application/json'}
    data = {
        "chat_id":to_id,
        "message":message
    }
    res = requests.post('http://0.0.0.0:5000/send_message',headers=Headers,data=json.dumps(data))