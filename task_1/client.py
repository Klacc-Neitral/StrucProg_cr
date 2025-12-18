import asyncio
import time

import aiohttp
import psutil
import requests

from urls import URLS

ASYNC_URL = "http://127.0.0.1:8081/parse"
THREAD_URL = "http://127.0.0.1:8085/parse"

async def async_request(session, url):
    async with session.post(ASYNC_URL, json={"url": url}) as resp:
        return await resp.json()

async def run_async_client():
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(async_request(session, u)) for u in URLS]
        return await asyncio.gather(*tasks)

def async_client():
    return asyncio.run(run_async_client())

def thread_request(url):
    resp = requests.post(THREAD_URL, json={"url": url})
    return resp.json()

def run_thread_client():
    results = []
    for url in URLS:
        results.append(thread_request(url))
    return results

def get_benchmark(fn):
    process = psutil.Process()
    ram_before = process.memory_info().rss
    cpu_before = psutil.cpu_percent(interval=None)

    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start

    ram_after = process.memory_info().rss
    cpu_after = psutil.cpu_percent(interval=None)

    return {
        "result": result,
        "time": elapsed,
        "ram": ram_after - ram_before,
        "cpu": cpu_after - cpu_before
    }

if __name__ == "__main__":
    async_metrics = get_benchmark(async_client)

    thread_metrics = get_benchmark(run_thread_client)

    print(f"Время async:  {async_metrics['time']:.3f} сек")
    print(f"Время thread: {thread_metrics['time']:.3f} сек\n")

    print(f"память async:  {async_metrics['ram'] / 1024 / 1024:.2f} МБ")
    print(f"память thread: {thread_metrics['ram'] / 1024 / 1024:.2f} МБ\n")

    print(f"процессор async:  {async_metrics['cpu']} %")
    print(f"процессор thread: {thread_metrics['cpu']} %\n")

    print("Ответы async-сервера:", async_metrics["result"])
    print("Ответы thread-сервера:", thread_metrics["result"])