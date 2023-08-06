from flask import Flask
from flask_sock import Sock
from flask_cors import CORS
import subprocess
import sys
import os

app = Flask(__name__)
sock = Sock(app)
CORS(app)


@sock.route("/snowsant")
def snowsant(ws):
    # 启动进程，记下连接
    p = subprocess.Popen(
        [sys.executable, "run.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=0,
    )

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
