import csv
import aiofiles

def write_to_csv(filepath, products):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Название товара', 'Цена'])
        writer.writerows(products)

async def write_to_csv_async(filepath, products):
    rows = [f"{name};{price}" for name, price in products]

    async with aiofiles.open(filepath, 'w', encoding='utf-8', newline='') as f:
        await f.write("Название товара;Цена\n")
        await f.write("\n".join(rows))
