from flask import Flask, jsonify
import requests
import base64
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
PORT = 4000

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
stk_url = os.getenv('STK_URL')
auth_url = os.getenv('AUTH_URL')
pass_key = os.getenv('PASS_KEY')
short_code = os.getenv('SHORT_CODE')
callback_url = os.getenv('CALLBACK_URL')


def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = short_code + pass_key + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode('utf-8')).decode('utf-8')
    return encoded_string, timestamp


def get_token():
    auth = f"{consumer_key}:{consumer_secret}"
    encoded_auth = base64.b64encode(auth.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_auth}"
    }
    response = requests.get(auth_url, headers=headers)
    response.raise_for_status()
    return response.json().get("access_token")


@app.route('/stk', methods=['GET'])
def stk_push():
    try:
        token = get_token()
        password, timestamp = generate_password()

        req_body = {
            "BusinessShortCode": short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",
            "PartyA": "254792867200",
            "PartyB": short_code,
            "PhoneNumber": "254792867200",
            "CallBackURL": callback_url,
            "AccountReference": "Test",
            "TransactionDesc": "Test"
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(stk_url, json=req_body, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())

    except Exception as e:
        print(e)
        return jsonify({"error": "STK push request failed"}), 500


if __name__ == '__main__':
    app.run(port=PORT)
