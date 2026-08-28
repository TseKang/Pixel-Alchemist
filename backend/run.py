"""
启动脚本 - 启动前清理占用端口的进程
"""
import sys
import subprocess
import socket
import time
from app.config import settings


def kill_port(port: int):
    """清理占用指定端口的进程"""
    if sys.platform == "win32":
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                print(f"Killed process {pid} on port {port}")
    else:
        result = subprocess.run(
            ["fuser", "-k", f"{port}/tcp"],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            print(f"Killed processes on port {port}: {result.stdout.strip()}")
        else:
            print(f"Cleaned up port {port}")


def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port_free(port: int, timeout: int = 10):
    """等待端口释放，超时返回 False"""
    for i in range(timeout):
        if not is_port_in_use(port):
            return True
        print(f"Waiting for port {port} to be free... ({i+1}/{timeout})")
        time.sleep(1)
    return False


if __name__ == "__main__":
    if is_port_in_use(settings.port):
        print(f"Port {settings.port} is in use, cleaning up...")
        kill_port(settings.port)
        if not wait_for_port_free(settings.port):
            print(f"ERROR: Port {settings.port} is still in use after cleanup")
            sys.exit(1)

    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
