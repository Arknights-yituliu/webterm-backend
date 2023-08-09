from flask import Flask
from flask_sock import Sock
from flask_cors import CORS
import subprocess
import sys
import os
from threading import Lock

app = Flask(__name__)
sock = Sock(app)
CORS(app)


p_count = 0
P_LIMIT = 15

lock = Lock()


@app.route("/snowsant/p")
def process_count():
    global p_count
    return {"p_count": p_count, "P_LIMIT": P_LIMIT}


@sock.route("/snowsant")
def snowsant(ws):
    global lock
    global p_count
    global P_LIMIT
    if p_count >= P_LIMIT:
        return

    # 启动进程，记下连接
    p = subprocess.Popen(
        [sys.executable, "run.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=0,
    )

    with lock:
        p_count += 1

    # 输入和输出处理
    while True:
        try:
            # 非阻塞地读输出
            output = os.read(p.stdout.fileno(), 1024)
            ws.send(output)

            # 写输入
            input = ws.receive()
            p.stdin.write(input + "\n")
        except Exception as e:
            p.terminate()
            break

    with lock:
        p_count -= 1
