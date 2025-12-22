import asyncio
import os
import aiofiles

HOST = "127.0.0.1"
PORT = 9001
TEST_DIR = "test_files"

async def count_lines_in_file(path: str) -> int:
    count = 0
    async with aiofiles.open(path, "r") as f:
        async for _ in f:
            count += 1
    return count

async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
):
    try:
        filename = (await reader.read(1024)).decode().strip()
        filepath = os.path.join(TEST_DIR, filename)

        if not os.path.isfile(filepath):
            writer.write(b"ERROR: file not found\n")
            await writer.drain()
            return

        lines = await count_lines_in_file(filepath)
        writer.write(f"{lines}\n".encode())
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print("Async server running on port", PORT)

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
