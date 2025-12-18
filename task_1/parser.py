from bs4 import BeautifulSoup


def extract_product_data(html_content):
    if not html_content:
        return [], 0.0

    soup_instance = BeautifulSoup(html_content, 'html.parser')
    return process_product_cards(soup_instance)


def extract_product_name(card_element):
    title_link = card_element.select_one('.set-card__title a')
    return title_link.get_text(strip=True) if title_link else None


def extract_product_price(card_element):

    meta_price = card_element.select_one('meta[itemprop="price"]')
    if meta_price and meta_price.has_attr('content'):
        return float(meta_price['content'])

    price_text_element = card_element.select_one('.set-card__price')
    if price_text_element:
        price_text = price_text_element.get_text()
        filtered_chars = [ch for ch in price_text if ch.isdigit() or ch == '.']
        numeric_string = ''.join(filtered_chars)
        return float(numeric_string) if numeric_string else 0.0

    return 0.0


def process_product_cards(soup_instance):
    product_cards = soup_instance.select('div.set-card')
    parsed_results = []
    page_total = 0.0

    for product_card in product_cards:
        try:
            item_name = extract_product_name(product_card)
            if not item_name:
                continue

            item_price = extract_product_price(product_card)

            parsed_results.append([item_name, item_price])
            page_total += item_price
        except (ValueError, AttributeError):
            continue

    return parsed_results, page_total