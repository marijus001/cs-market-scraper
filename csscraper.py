import requests
from bs4 import BeautifulSoup
import json
import csv

def calculate_profit_margin(lowest_bid, lowest_listing):
    return lowest_listing - lowest_bid

def get_item_data(start):
    url = f'https://steamcommunity.com/market/search/render/?query=&appid=730&start={start}&count=100&currency=3'
    response = requests.get(url, headers=headers)
    return response

def parse_item_data(response):
    data = json.loads(response.text)
    soup = BeautifulSoup(data['results_html'], 'html.parser')
    return soup

def is_profitable(lowest_bid_offer, lowest_price_listing):
    profit_margin = calculate_profit_margin(lowest_bid_offer, lowest_price_listing)
    return profit_margin > 0

APP_ID = '730'
STEAM_TAX_DIVISOR = 1.15
MIN_PRICE_EUR = 10

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

profitable_items = []

start = 0
has_more_items = True

while has_more_items:
    response = get_item_data(start)

    if response.status_code == 200:
        soup = parse_item_data(response)

        items = soup.find_all('a', {'class': 'market_listing_row_link'})

        for item in items:
            # Extract item name
            name = item.find('span', {'class': 'market_listing_item_name'}).text

            # Extract lowest bid offer (no tax applied)
            bid = item.find('span', {'class': 'market_commodity_orders_header_promote'})
            if bid:
                lowest_bid_offer = float(bid.text.strip().split(' ')[0].replace(',', ''))
            else:
                continue

            # Extract lowest price listing (tax applied)
            price = item.find('span', {'class': 'market_listing_price market_listing_price_with_fee'})
            if price:
                lowest_price_listing = (float(price.text.strip().split(' ')[0].replace(',', '')) / STEAM_TAX_DIVISOR) - 0.01
            else:
                continue

            # Filter items above 10 euros and sort by descending price
            if lowest_price_listing >= MIN_PRICE_EUR and is_profitable(lowest_bid_offer, lowest_price_listing):
                profitable_items.append({
                    'name': name,
                    'lowest_bid_offer': lowest_bid_offer,
                    'lowest_price_listing': lowest_price_listing,
                    'profit_margin': calculate_profit_margin(lowest_bid_offer, lowest_price_listing)
                })

        # Check if there are more items
        response_json = response.json()
        has_more_items = response_json.get('has_more', False)
        start += 100

    else:
        print(f'Error {response.status_code}: Failed to fetch market data.')
        break

# Sort items by descending price
profitable_items.sort(key=lambda x: x['lowest_price_listing'], reverse=True)

# Print profitable items
for item in profitable_items:
    print(f"Item: {item['name']}")
    print(f"Lowest Bid Offer: €{item['lowest_bid_offer']:.2f}")
    print(f"Lowest Price Listing: €{item['lowest_price_listing']:.2f}")
    print(f"Profit Margin: €{item['profit_margin']:.2f}")
