import requests
import re
import time
import logging
import json
from requests.auth import HTTPDigestAuth
import secrets

# CONFIGURATIONS
DEVICE_IP = "192.168.88.132"
USERNAME = "admin"
PASSWORD = "plamongan17"
LOGIN_URL = f"http://{DEVICE_IP}/doc/page/login.asp"
USERINFO_URL_TEMPLATE = f"http://{DEVICE_IP}/ISAPI/AccessControl/UserInfo/Search?format=json&security=1&iv={{iv}}"
LOG_FILE = "acs_agent.log"

# SETUP LOGGING
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

# SESSION OBJECT
session = requests.Session()

# def get_iv_token():
#     logging.info("Mengambil IV token dari WebApp")
    
#     try:
#         response = session.get(LOGIN_URL, timeout=5)
#         if response.status_code == 200:
#             logging.info("Berhasil akses login page")
#             # Biasanya IV disisipkan di HTML source WebApp
#             # match = re.search(r'var iv="(.*?)";', response.text)
#             match = re.search(r'var iv=["\']([a-f0-9]+)["\']', response.text)
#             logging.info(response.text)
#             if match:
#                 iv = match.group(1)
#                 logging.info(f"IV token ditemukan: {iv}")
#                 return iv
#             else:
#                 logging.error("IV token tidak ditemukan!")
#         else:
#             logging.error(f"Gagal akses login page: {response.status_code}")
#     except Exception as e:
#         logging.error(f"Error saat ambil IV: {e}")
#     return None


def generate_iv_secure():
    # Generate 16-byte cryptographically secure random
    iv_bytes = secrets.token_bytes(16)
    iv_hex = iv_bytes.hex()
    logging.info(f"Generated secure IV: {iv_hex}")
    return iv_hex

# iv = generate_iv_secure()
# print("Secure IV:", iv)

# def get_iv_from_api(device_ip, username, password):
#     iv_url = f"http://{device_ip}/ISAPI/Security/IVToken"

#     try:
#         response = requests.get(
#             iv_url,
#             auth=HTTPBasicAuth(username, password),
#             verify=False,
#             timeout=5
#         )

#         if response.status_code == 200:
#             return response.text.strip()  # IV langsung di body response
#         else:
#             print(f"Gagal mengambil IV. Kode status: {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"Error: {e}")
#         return None

# # Contoh penggunaan
# iv = get_iv_from_api("192.168.88.132", "admin", "password123")
# print("IV dari API:", iv)

def login_webapp():
    logging.info("Login ke webapp Hikvision")
    login_api = f"http://{DEVICE_IP}/ISAPI/Security/userCheck"
    headers = {"Content-Type": "application/xml"}

    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
    <UserCheck>
    <UserName>{USERNAME}</UserName>
    <Password>{PASSWORD}</Password>
    </UserCheck>"""

    response = session.post(login_api, data=payload, headers=headers, timeout=5)
    if response.status_code == 200:
        logging.info("Login webapp sukses")
        return True
    else:
        logging.error(f"Login gagal: {response.status_code}")
        return False

def poll_userinfo():
    # iv = get_iv_token()
    # iv = get_iv_from_api("192.168.88.132", "admin", "plamongan17")
    iv = generate_iv_secure()
    if not iv:
        logging.error("Gagal ambil IV token, polling dihentikan sementara")
        return

    url = USERINFO_URL_TEMPLATE.format(iv=iv)
    try:
        response = session.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=10)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Data UserInfo: {json.dumps(data)}")
            process_data(data)
        else:
            logging.error(f"Polling error: {response.status_code}")
    except Exception as e:
        logging.error(f"Error polling UserInfo: {e}")

def process_data(data):
    # Proses data untuk dikirim ke ADMS atau database
    logging.info("Processing data")
    # Tambahkan logic forwarding ke server pusat di sini
    pass

def main_loop():
    while True:
        try:
            poll_userinfo()
            time.sleep(60)  # Poll setiap 1 menit
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main_loop()