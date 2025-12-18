from flask import Flask, request, jsonify
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

from parser import parse_content
from urls import OUTPUT_FILE_THREADS
from utils import write_to_csv

app = Flask(__name__)

items_buffer = []
overall_sum = 0.0
data_protector = threading.Lock()

task_dispatcher = ThreadPoolExecutor(max_workers=50)


def download_and_process(web_address):
    page_content = requests.get(web_address, timeout=10)
    html_data = page_content.text
    return parse_content(html_data)


def process_single_page(page_url):
    global overall_sum
    products_list, page_total = download_and_process(page_url)

    with data_protector:
        items_buffer.extend(products_list)
        overall_sum += page_total
        write_to_csv(OUTPUT_FILE_THREADS, items_buffer)
        items_buffer.clear()

    return len(products_list), page_total


@app.route("/parse", methods=["POST"])
def api_processor():
    request_data = request.get_json()
    target_url = request_data["url"]
    print(f"[THREAD SERVER] Обработка: {target_url}")

    future_result = task_dispatcher.submit(process_single_page, target_url)
    items_count, subtotal = future_result.result()

    return jsonify({
        "count": items_count,
        "sum": subtotal
    })


def start_service():
    """Запуск сервиса"""
    print("[THREAD SERVER] HTTP многопоточный сервер запущен на 127.0.0.1:8085")
    app.run(host="127.0.0.1", port=8085, threaded=True)


if __name__ == "__main__":
    start_service()