from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Initialize Selenium WebDriver
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    service = Service(r'C:\Webdrivers\chromedriver-win64\chromedriver.exe')  # Ensure chromedriver is in your PATH
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def crawl_website(start_url):
    driver = initialize_driver()
    driver.get(start_url)

    visited_links = set()
    to_visit_links = set([start_url])
    website_content = []

    while to_visit_links:
        current_url = to_visit_links.pop()
        if current_url in visited_links:
            continue

        try:
            driver.get(current_url)
            time.sleep(2)  # Wait for the page to load
            visited_links.add(current_url)

            # Extract page content
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            website_content.append({"url": current_url, "content": page_text})

            # Find all links on the page
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute('href')
                if href and href.startswith(start_url) and href not in visited_links:
                    to_visit_links.add(href)

        except Exception as e:
            print(f"Error processing {current_url}: {e}")

    driver.quit()
    return website_content

# Save content to a file
def save_content(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for page in content:
            f.write(f"URL: {page['url']}\n")
            f.write(f"Content:\n{page['content']}\n\n")

if __name__ == "__main__":
    start_url = "https://commediaindia.com"  # Replace with the target website URL
    content = crawl_website(start_url)
    save_content(content, "website_content.txt")
    print("Content saved to website_content.txt")
