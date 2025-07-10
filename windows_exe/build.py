import subprocess, threading, webview, os, sys


os.makedirs("chats", exist_ok=True)
os.makedirs("documents", exist_ok=True)

from dotenv import load_dotenv

load_dotenv("secrets.env")
redis_pass = os.getenv("DB_PASSWORD")

with open("redis.conf.template", "r") as template:
    conf = template.read().replace("$REDIS_PASSWORD", redis_pass)

with open("redis.conf", "w") as final_conf:
    final_conf.write(conf)



def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def start_backend():
    subprocess.Popen([resource_path("redis-server.exe"), resource_path("redis.conf")])
    subprocess.Popen(["python", resource_path("backend/main.py")])

if __name__ == "__main__":
    threading.Thread(target=start_backend).start()
    webview.create_window("Mi App", "http://127.0.0.3:13001/main.html", width=1000, height=700)
    webview.start()
