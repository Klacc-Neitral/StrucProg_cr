import os
import socket
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"
PORT = 9002
TEST_DIR = "test_files"

def count_lines_in_file(path: str) -> int:
    with open(path, "r") as f:
        return sum(1 for _ in f)

def handle_connection(conn: socket.socket):
    try:
        filename = conn.recv(1024).decode().strip()
        filepath = os.path.join(TEST_DIR, filename)

        if not os.path.isfile(filepath):
            conn.sendall(b"ERROR: file not found\n")
            return

        lines = count_lines_in_file(filepath)
        conn.sendall(f"{lines}\n".encode())
    finally:
        conn.close()

def main():
    executor = ThreadPoolExecutor(max_workers=1000)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1000)

    print("Thread server running on port", PORT)

    while True:
        conn, _ = sock.accept()
        executor.submit(handle_connection, conn)

if __name__ == "__main__":
    main()
