import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from urllib.parse import urljoin

def scrape_website(base_url):
    """
    Scrapes a website, extracts text from all pages, and downloads all PDFs.

    Args:
        base_url (str): The base URL of the website to scrape.
    """
    output_dir = "scraped_data"
    os.makedirs(output_dir, exist_ok=True)

    visited_urls = set()
    urls_to_visit = {base_url}

    while urls_to_visit:
        url = urls_to_visit.pop()
        if url in visited_urls:
            continue

        try:
            response = requests.get(url)
            response.raise_for_status()
            visited_urls.add(url)

            try:
                soup = BeautifulSoup(response.content, 'html5lib')
            except Exception as e:
                print(f"Error parsing {url}: {e}")
                continue

            # Extract text from the page
            filename = os.path.join(output_dir, f"{urllib.parse.quote_plus(url)}.txt")
            if not os.path.exists(filename):
                page_text = soup.get_text(separator='\n', strip=True)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(page_text)
                print(f"Scraped text from: {url}")

            # Find and download PDFs
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    pdf_url = urljoin(url, href)
                    pdf_filename = os.path.join(output_dir, os.path.basename(pdf_url))
                    if not os.path.exists(pdf_filename):
                        try:
                            pdf_response = requests.get(pdf_url)
                            pdf_response.raise_for_status()
                            with open(pdf_filename, 'wb') as f:
                                f.write(pdf_response.content)
                            print(f"Downloaded PDF: {pdf_url}")
                        except requests.exceptions.RequestException as e:
                            print(f"Error downloading PDF {pdf_url}: {e}")


            # Find and add new links to visit
            for link in soup.find_all('a', href=True):
                href = link['href']
                new_url = urljoin(url, href)
                if new_url.startswith(base_url) and new_url not in visited_urls:
                    urls_to_visit.add(new_url)

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")
    
    print("\nScraping complete.")

if __name__ == "__main__":
    school_website_url = "https://www.dovedaleprimary.co.uk/"
    scrape_website(school_website_url)
