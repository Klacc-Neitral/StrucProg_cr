from bs4 import BeautifulSoup

def parse_content(html):
    if not html: return [], 0.0
    soup = BeautifulSoup(html, 'html.parser')

    cards = soup.select('div.set-card')

    results = []
    page_sum = 0.0

    for card in cards:
        try:
            title_tag = card.select_one('.set-card__title a')
            if not title_tag: continue
            name = title_tag.get_text(strip=True)

            meta_price = card.select_one('meta[itemprop="price"]')
            if meta_price:
                price_val = float(meta_price['content'])
            else:
                price_tag = card.select_one('.set-card__price')
                if price_tag:
                    clean = "".join([c for c in price_tag.get_text() if c.isdigit() or c == '.'])
                    price_val = float(clean) if clean else 0.0
                else:
                    price_val = 0.0

            results.append([name, price_val])
            page_sum += price_val
        except:
            continue

    return results, page_sum