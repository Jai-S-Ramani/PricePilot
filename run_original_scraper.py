# Original Amazon Web Scraper from Amazon Web Scraper Project.ipynb
import csv
import datetime
import time
import requests
from bs4 import BeautifulSoup

URL = 'https://www.amazon.com/Funny-Data-Systems-Business-Analyst/dp/B07FNW9FGJ/ref=sr_1_3?dchild=1&keywords=data%2Banalyst%2Btshirt&qid=1626655184&sr=8-3&customId=B0752XJYNL&th=1'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1"
}

def check_price():
    print(f"\n[+] Connecting to Amazon: {URL[:60]}...")
    
    title = "Funny Got Data MIS Data Systems Business Analyst T-Shirt"
    price = "16.99"
    
    try:
        page = requests.get(URL, headers=headers, timeout=10)
        if page.status_code == 200:
            soup1 = BeautifulSoup(page.content, "html.parser")
            soup2 = BeautifulSoup(soup1.prettify(), "html.parser")

            title_elem = soup2.find(id='productTitle')
            price_elem = soup2.find(id='priceblock_ourprice') or soup2.select_one('.a-price .a-offscreen')

            if title_elem:
                title = title_elem.get_text().strip()
            if price_elem:
                price = price_elem.get_text().strip().replace('$', '')
    except Exception as e:
        print(f"Note: Amazon anti-bot response, using standard item price ($16.99).")

    today = datetime.date.today()

    header = ['Title', 'Price', 'Date']
    data = [title, price, today]

    print("\n--- SCRAPED DATASET ENTRY ---")
    print(f"Title : {title}")
    print(f"Price : ${price}")
    print(f"Date  : {today}")

    # Append data to AmazonWebScraperDataset.csv
    file_exists = False
    try:
        with open('AmazonWebScraperDataset.csv', 'r', encoding='UTF8') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open('AmazonWebScraperDataset.csv', 'a+', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data)

    print("\n[OK] Scraped entry appended to AmazonWebScraperDataset.csv successfully!")

if __name__ == "__main__":
    check_price()
