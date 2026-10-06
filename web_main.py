import os
import socket
import tempfile
from pathlib import Path

import uvicorn

from app.web.jobs import JobQueue
from app.web.server import create_app

# 6000 番は X11 用の予約番号で、Chrome / Firefox が接続を拒否するため使わない
DEFAULT_PORT = 6100


def lan_ip() -> str | None:
    # UDP の connect は実際には通信しない。経路選択の結果から自分の LAN 側 IP を得る
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("192.0.2.1", 9))
            return sock.getsockname()[0]
        except OSError:
            return None


def main():
    port = int(os.environ.get("MOJI_PORT", DEFAULT_PORT))
    password = os.environ.get("MOJI_PASSWORD") or None

    upload_dir = Path(tempfile.gettempdir()) / "moji-okoshi-uploads"
    app = create_app(JobQueue(), upload_dir=upload_dir, password=password)

    print(f"このPCから:     http://localhost:{port}")
    ip = lan_ip()
    if ip:
        print(f"同じネットワークから: http://{ip}:{port}")
    print("パスワード: " + ("あり" if password else "なし"))
    print("止めるときは、このウィンドウを閉じるか Ctrl+C を押してください。")

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
