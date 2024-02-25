import requests
from bs4 import BeautifulSoup
import csv

# Function to fetch the content of a page
def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to fetch page: {url} with status code {response.status_code}")
        return None

# Function to extract book information from its detail page
def extract_book_info(book_page_soup):
    title = book_page_soup.find('h1').text
    price_text = book_page_soup.find('p', class_='price_color').text
    # Remove the pound symbol from the price string to avoid weird characters in the CSV file; UTF-8 encoding doesn't seem to handle it well
    price = price_text.replace('Â£', '').replace('£', '')
    stock = book_page_soup.find('p', class_='instock availability').text.strip()
    description_tag = book_page_soup.find('div', id='product_description')
    description = description_tag.find_next_sibling('p').text if description_tag else 'No description'
    
    # Determine the star rating
    star_rating_tag = book_page_soup.find('p', class_='star-rating')
    ratings = {"One": "1", "Two": "2", "Three": "3", "Four": "4", "Five": "5"}
    star_rating = "No rating"  # Default if not found
    for rating in ratings:
        if rating in star_rating_tag['class']:
            star_rating = ratings[rating]
            break

    return title, price, star_rating, stock, description

# Main scraper function to iterate over book listing pages and extract data
def scrape_books(base_url):
    books_data = []
    webpages_scraped = 0
    books_scraped = 0
    for i in range(1, 51):  # Number of pages to scrape
        page_url = f"{base_url}/catalogue/page-{i}.html"
        print(f"Fetching page {i}")
        soup = fetch_page(page_url)
        if soup:
            webpages_scraped += 1
            books = soup.find_all('article', class_='product_pod')
            for book in books:
                book_url_suffix = book.find('h3').find('a')['href']
                book_url = f"{base_url}/catalogue/{book_url_suffix.lstrip('/')}"
                print(f"Fetching book details from {book_url}")
                book_soup = fetch_page(book_url)
                if book_soup:
                    books_data.append(extract_book_info(book_soup) + (book_url,))
                    books_scraped += 1
    
    # Save the extracted data to a CSV file
    with open('books_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Star Rating', 'Availability', 'Description', 'URL'])
        writer.writerows(books_data)

    # Print a summary of the run
    print(f"\nSuccessful run!")
    print(f"Total webpages successfully scraped: {webpages_scraped}")
    print(f"Total books successfully scraped: {books_scraped}")

# Base URL of the site to scrape
BASE_URL = 'http://books.toscrape.com'

# Start the scraping process
scrape_books(BASE_URL)
