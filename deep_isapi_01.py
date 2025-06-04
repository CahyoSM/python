import os
import requests
from requests.auth import HTTPDigestAuth
import json
from datetime import datetime
import time
import threading
import xmltodict


class RealtimeAttendanceMonitor:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.base_url = f"http://{self.ip}/ISAPI/"
        self.session = None
        self.running = False
        self.last_event_id = None
        self.callback = None
        
    def connect(self):
        """Membuat koneksi dengan autentikasi Digest"""
        try:
            self.session = requests.Session()
            self.session.auth = HTTPDigestAuth(self.username, self.password)
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
            
            # Test connection
            test_url = f"{self.base_url}AccessControl/Capabilities"
            response = self.session.get(test_url, timeout=5)
            
            if response.status_code == 401:
                raise Exception("Autentikasi gagal - periksa username/password")
            elif response.status_code != 200:
                raise Exception(f"Koneksi gagal dengan kode status: {response.status_code}")
                
            print("Koneksi berhasil dengan perangkat access control DS-KT1342")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error koneksi: {str(e)}")
            return False
    
    def get_initial_events(self, limit=1):
        """Mendapatkan event terakhir sebagai referensi awal"""

        endpoint = "AccessControl/AcsEvent"
        params = {
                "AcsEventCond": {
                    "searchID": "f123402329784e958264b5ff7da7e7e2",
                    "searchResultPosition": 0,
                    "maxResults": 24,
                    "major": 0,
                    "minor": 0,
                    "startTime": "2025-06-03T00:00:00+07:00",
                    "endTime": "2025-06-03T23:59:59+07:00",
                    "timeReverseOrder": 1
                }
            }   
        try:
            response = self.session.get(self.base_url + endpoint, params=params)
            response.raise_for_status()
            
            events = response.json()
            if events.get("AccessControlEvent"):
                self.last_event_id = events["AccessControlEvent"][0].get("employeeNoString")
                return events["AccessControlEvent"][0]
            return None
        except requests.exceptions.RequestException as e:
            print(f"Gagal mendapatkan event awal: {str(e)}")
            return None
    
    def start_realtime_monitoring(self, callback=None, interval=2):
        """Memulai monitoring realtime dengan callback"""
        if not self.session:
            print("Koneksi belum diinisialisasi")
            return False
            
        self.callback = callback
        self.running = True
        
        # Dapatkan event terakhir sebagai referensi
        last_event = self.get_initial_events()
        if last_event:
            print("\nEvent terakhir yang tercatat:")
            self.print_event(last_event)
        
        print("\nMemulai monitoring realtime... (Tekan Ctrl+C untuk berhenti)")
        
        # Mulai thread untuk monitoring
        monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        monitor_thread.start()
        
        return True
    
    def _monitor_loop(self, interval):
        """Loop utama untuk monitoring realtime"""
        while self.running:
            try:
                self.check_new_events()
                time.sleep(interval)
            except Exception as e:
                print(f"Error dalam monitoring loop: {str(e)}")
                time.sleep(5)  # Tunggu sebelum mencoba lagi
    
    def check_new_events(self):
        """Memeriksa event baru sejak terakhir diperiksa"""
        endpoint = "AccessControl/Event/transaction"
        params = {
            "numOfRecords": 10,  # Ambil 10 terbaru untuk memastikan tidak ada yang terlewat
            "searchID": "2",      # ID pencarian berbeda dari inisialisasi
            "searchResultPosition": 0,
            "order": "desc"
        }
        
        try:
            response = self.session.get(self.base_url + endpoint, params=params)
            response.raise_for_status()
            
            events = response.json()
            if not events.get("AccessControlEvent"):
                return
                
            new_events = []
            
            # Cari event baru sejak terakhir diperiksa
            for event in events["AccessControlEvent"]:
                if self.last_event_id and event.get("employeeNoString") == self.last_event_id:
                    break
                new_events.append(event)
            
            # Proses event baru dari yang terlama ke terbaru
            for event in reversed(new_events):
                self.last_event_id = event.get("employeeNoString")
                self.print_event(event)
                
                # Panggil callback jika ada
                if self.callback:
                    self.callback(event)
                    
        except requests.exceptions.RequestException as e:
            print(f"Gagal memeriksa event baru: {str(e)}")

    def trial_event(self):
        """Mencetak event untuk debugging"""
        """https://192.168.88.132/ISAPI/Security/questionConfiguration?security=1&iv=a49f25d67013a807614ea551a09db015"""
        
        iv = self.generate_iv()  
        endpoint = f"AccessControl/AcsEvent/capabilities?format=json"
        endpoint2 = f"AccessControl/AcsEvent?format=json&security=1"
        print(f"Endpoint untuk trial event: {endpoint2}")

        parammeter = {
            "AcsEventCond": {
                "searchID": "f123402329784e958264b5ff7da7e7e2",
                "searchResultPosition": 0,
                "maxResults": 24,
                "major": 0,
                "minor": 0,
                "startTime": "2025-06-03T00:00:00+07:00",
                "endTime": "2025-06-03T23:59:59+07:00",
                "timeReverseOrder": True
            }
            }

        # parammeter = "http://192.168.88.132/ISAPI/AccessControl/AcsEvent?format=json&security=1&iv=2e236218341f562ffbd451cfe847a885"
        response1 = self.session.get(self.base_url + endpoint, auth=HTTPDigestAuth("admin","plamongan17"))
        response1.raise_for_status()
        print(f"Response Text ep1: {response1.json()}...")  # Tampilkan sebagian teks untuk debugging

        response2 = self.session.post(self.base_url + endpoint2, params=parammeter, auth=HTTPDigestAuth("admin","plamongan17"),headers={"Content-Type": "application/json"},json=parammeter)
        response2.raise_for_status()
        print(f"Response Text ep2: {response2.json()}...")  # Tampilkan sebagian teks untuk debugging
        # print("Response untuk trial event diterima")
        # print(f"Status Code: {response.status_code}")
        # events = response.text
        # events = xmltodict.parse(events)


       # Navigasi ke daftar pertanyaan
        # questions = events['SecurityQuestion']['QuestionList']['Question']

    #     # Jika hanya satu Question, xmltodict tidak mengubahnya jadi list
    #     if isinstance(questions, dict):
    #         questions = [questions]

    #     # Tampilkan
    #     for q in questions:
    #         print(f"ID: {q['id']}, Mark: {q['mark']}")

        # if not events.get("AccessControlEvent"):
        #     return
        # try:
        #     event = {
        #         "time": datetime.now().isoformat(),
        #         "employeeNoString": "123456",
        #         "name": "John Doe",
        #         "cardNo": "987654321",
        #         "doorName": "Main Entrance",
        #         "currentVerifyMode": "Card",
        #         "eventStatus": "Success"
        #         }
        #     self.print_event(event)
        # except Exception as e:
        #     print(f"Error dalam trial event: {str(e)}")
        

    def generate_iv(self):
        """Menghasilkan IV untuk enkripsi (dummy function)"""
        # Implementasi sebenarnya tergantung pada algoritma enkripsi yang digunakan
        return os.urandom(16).hex()
    
    @staticmethod
    def print_event(event):
        """Mencetak detail event"""
        print("\n=== ABSENSI BARU ===")
        print(f"Waktu: {event.get('time', 'N/A')}")
        print(f"ID Karyawan: {event.get('employeeNoString', 'N/A')}")
        print(f"Nama: {event.get('name', 'N/A')}")
        print(f"Card No: {event.get('cardNo', 'N/A')}")
        print(f"Pintu: {event.get('doorName', 'N/A')}")
        print(f"Metode: {event.get('currentVerifyMode', 'N/A')}")
        print(f"Status: {event.get('eventStatus', 'N/A')}")
        print("===================")
    
    def stop_monitoring(self):
        """Menghentikan monitoring realtime"""
        self.running = False
        print("Monitoring realtime dihentikan")
    
    def close(self):
        """Menutup koneksi"""
        self.stop_monitoring()
        if self.session:
            self.session.close()
            self.session = None
            print("Koneksi ditutup")

if __name__ == "__main__":
    # Konfigurasi perangkat - sesuaikan dengan perangkat Anda
    DEVICE_IP = "192.168.88.132"
    USERNAME = "admin"
    PASSWORD = "plamongan17"
    
    # Contoh callback untuk menangani event baru
    def handle_new_event(event):
        # Disini bisa ditambahkan logika untuk menyimpan ke database,
        # mengirim notifikasi, dll.
        pass
    
    # Membuat monitor
    monitor = RealtimeAttendanceMonitor(DEVICE_IP, USERNAME, PASSWORD)
    
    try:
        # Inisialisasi koneksi
        if not monitor.connect():
            exit(1)
        
        monitor.trial_event()  # Untuk testing trial event

        # # Mulai monitoring realtime
        # monitor.start_realtime_monitoring(
        #     callback=handle_new_event,
        #     interval=1  # Cek setiap 1 detik
        # )
        
        # Biarkan program berjalan sampai dihentikan
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Pastikan koneksi ditutup
        monitor.close()