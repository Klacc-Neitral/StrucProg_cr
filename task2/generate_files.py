import os

BASE_DIR = "test_files"
FILES_COUNT = 100
LINES_PER_FILE = 1000

os.makedirs(BASE_DIR, exist_ok=True)

for i in range(1, FILES_COUNT + 1):
    path = os.path.join(BASE_DIR, f"file_{i}.txt")
    with open(path, "w", encoding="utf-8") as f:
        for line in range(1, LINES_PER_FILE + 1):
            f.write(f"{line}\n")

print(f"Создано {FILES_COUNT} файлов по {LINES_PER_FILE} строк")
