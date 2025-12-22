import asyncio
import socket
import time
import random
import os
import psutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
import signal

TEST_DIR = "test_files"
FILES = os.listdir(TEST_DIR)

ASYNC_PORT = 9001
THREAD_PORT = 9002


async def async_request():
    reader, writer = await asyncio.open_connection("127.0.0.1", ASYNC_PORT)
    name = random.choice(FILES)
    writer.write(name.encode())
    await writer.drain()
    await reader.readline()
    writer.close()
    await writer.wait_closed()

async def run_async_load(n: int):
    tasks = [asyncio.create_task(async_request()) for _ in range(n)]
    await asyncio.gather(*tasks)

def thread_request():
    s = socket.socket()
    s.connect(("127.0.0.1", THREAD_PORT))
    name = random.choice(FILES)
    s.sendall(name.encode())
    s.recv(1024)
    s.close()

def run_thread_load(n: int):
    with ThreadPoolExecutor(max_workers=n) as executor:
        futures = [executor.submit(thread_request) for _ in range(n)]
        for f in futures:
            f.result()
def monitor_process(proc: psutil.Process, stop_event, interval=0.01):
    peak_rss = 0

    while not stop_event.is_set():
        try:
            rss = proc.memory_info().rss
            peak_rss = max(peak_rss, rss)
        except psutil.NoSuchProcess:
            break
        time.sleep(interval)

    return peak_rss


def measure(fn, n, label, process: subprocess.Popen):
    print(f"\n=== {label}: {n} concurrent requests ===")

    proc = psutil.Process(process.pid)
    stop_event = threading.Event()
    peak_holder = {}

    def monitor():
        peak_holder["rss"] = monitor_process(proc, stop_event)

    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.start()

    t0 = time.time()
    fn(n)
    dt = time.time() - t0

    stop_event.set()
    monitor_thread.join()

    peak_mb = peak_holder["rss"] / 1024 / 1024

    print(f"Time: {dt:.2f} sec")
    print(f"Peak server memory: {peak_mb:.2f} MB")

def start_server(cmd):
    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == "__main__":
    N = 1000

    # ---- Async server ----
    async_server = start_server(["python", "async_server.py"])
    time.sleep(1)

    measure(
        lambda n: asyncio.run(run_async_load(n)),
        N,
        "AsyncIO server",
        async_server
    )

    async_server.send_signal(signal.SIGTERM)
    async_server.wait()

    thread_server = start_server(["python", "thread_server.py"])
    time.sleep(1)

    measure(
        run_thread_load,
        N,
        "Thread server",
        thread_server
    )

    thread_server.send_signal(signal.SIGTERM)
    thread_server.wait()
