from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import requests
import time
import re
import os
from bs4 import BeautifulSoup

# Function to initialize the WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(executable_path=r"C:\webdrivers\chromedriver-win64\chromedriver.exe")  # Replace with the path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to fetch the content of a page
def fetch_page_content(driver, url):
    driver.get(url)
    return driver.page_source

# Function to parse the main page and extract URLs
def extract_urls(driver, main_page_content, base_url):
    soup = BeautifulSoup(main_page_content, 'html.parser')
    urls = set()  # Use a set to avoid duplicate URLs
    for link in soup.find_all('a', href=True):
        url = urljoin(base_url, link['href'])
        urls.add(url)
    return list(urls)

# Function to handle 'View More' buttons and click them
def click_view_more_buttons(driver):
    try:
        while True:
            # Adjust the locator as per the 'View More' button on your target website
            view_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View More')]"))
            )
            view_more_button.click()
            time.sleep(2)  # Adjust the sleep time as necessary
    except Exception as e:
        print("No more 'View More' buttons or an error occurred: ", e)

# Function to fetch title, content, and tables from a page
def fetch_title_content_and_tables(driver, url):
    page_content = fetch_page_content(driver, url)
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Extract title
    title = soup.find('title').text if soup.find('title') else 'No Title'
    
    # Extract body content
    paragraphs = soup.find_all('p')
    body_content = '\n'.join(p.get_text() for p in paragraphs)
    
    # Extract tables
    tables = []
    for table in soup.find_all('table'):
        headers = [header.get_text() for header in table.find_all('th')]
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.get_text() for cell in row.find_all('td')]
            if cells:
                rows.append(cells)
        if (headers, rows) not in tables:  # Avoid duplicate tables
            tables.append((headers, rows))
    
    return title, body_content, tables

# Function to check robots.txt for disallowed paths
def is_allowed_by_robots_txt(base_url, user_agent):
    robots_url = urljoin(base_url, '/robots.txt')
    try:
        robots_response = requests.get(robots_url, headers={'User-Agent': user_agent})
        robots_response.raise_for_status()
        robots_txt = robots_response.text
        disallowed_paths = re.findall(r'Disallow: (.*)', robots_txt)
        for path in disallowed_paths:
            if path.strip() and path in base_url:
                return False
        return True
    except requests.RequestException:
        return False  # Assume disallowed if robots.txt cannot be fetched

# Main function to scrape and save content
def scrape_and_save(main_url, output_file, user_agent='MyScraperBot/1.0'):
    driver = init_driver()
    
    if not is_allowed_by_robots_txt(main_url, user_agent):
        print(f"Scraping is disallowed by robots.txt for {main_url}")
        driver.quit()
        return
    
    main_page_content = fetch_page_content(driver, main_url)
    urls = extract_urls(driver, main_page_content, main_url)
    
    scraped_urls = set()  # Keep track of scraped URLs
    with open(output_file, 'w', encoding='utf-8') as file:
        for url in urls:
            if url in scraped_urls:
                continue  # Skip already scraped URLs
            scraped_urls.add(url)
            try:
                # Handle 'View More' buttons if any
                click_view_more_buttons(driver)
                
                title, content, tables = fetch_title_content_and_tables(driver, url)
                file.write(f"URL: {url}\nTitle: {title}\n\n{content}\n\n")
                for headers, rows in tables:
                    file.write("Table:\n")
                    file.write("\t".join(headers) + "\n")
                    for row in rows:
                        file.write("\t".join(row) + "\n")
                    file.write("\n")
                file.write(f"{'='*80}\n\n")
                print(f"Saved content from {url}")
                time.sleep(2)  # Delay between requests
            except Exception as e:
                print(f"An error occurred with {url}: {e}")
    
    driver.quit()

# Example usage
main_url = 'https://www.example.com'  # Replace with the actual main URL
output_file = 'content.txt'
scrape_and_save(main_url, output_file)
