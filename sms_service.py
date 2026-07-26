import requests

import streamlit as st

API_TOKEN = st.secrets["SMS_API_TOKEN"]

def send_sms(phone_number, message):

    url = "https://www.iprogsms.com/api/v1/sms_messages"

    payload = {
        "api_token": API_TOKEN,
        "phone_number": phone_number,
        "message": message
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        print("Status:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            return True

        return False        

    except Exception as e:

        print("SMS Error:", e)

        return False