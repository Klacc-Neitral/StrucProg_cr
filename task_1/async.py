import asyncio
import aiohttp
from aiohttp import web

from parser import parse_content
from urls import OUTPUT_FILE_ASYNC
from utils import write_to_csv_async


class AsyncDataProcessor:

    def __init__(self):
        self.data_cache = []
        self.cumulative_amount = 0.0
        self.processing_lock = asyncio.Lock()

    async def fetch_webpage(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def handle_parsing_request(self, request):
        json_data = await request.json()
        webpage_url = json_data["url"]
        print(f"[ASYNC ENGINE] Processing: {webpage_url}")

        html_content = await self.fetch_webpage(webpage_url)
        items_collection, page_sum = parse_content(html_content)

        async with self.processing_lock:
            self.data_cache.extend(items_collection)
            self.cumulative_amount += page_sum
            await write_to_csv_async(OUTPUT_FILE_ASYNC, self.data_cache)
            self.data_cache.clear()

        return web.json_response({
            "count": len(items_collection),
            "sum": page_sum
        })


def initialize_web_app():
    processor = AsyncDataProcessor()
    app_instance = web.Application()

    app_instance.router.add_post(
        "/parse",
        processor.handle_parsing_request
    )

    return app_instance


def start_web_service():
    application = initialize_web_app()
    print("[ASYNC SERVER] Сервер запущен на 127.0.0.1:8081")
    web.run_app(application, host="127.0.0.1", port=8081)


if __name__ == "__main__":
    start_web_service()