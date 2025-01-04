import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_all_links(url, base_url):
    """ Get all links from a given URL """
    links = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        if link.startswith('/'):
            link = base_url + link
        if base_url in link:
            links.append(link)
    return links

def extract_tables_from_url(url):
    """ Extract all tables from a given URL """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = []
    for table in soup.find_all('table'):
        df = pd.read_html(str(table))[0]
        tables.append(df)
    return tables

def save_tables_to_txt(tables, filename):
    """ Save list of DataFrames (tables) to a text file """
    with open(filename, 'a') as f:
        for i, table in enumerate(tables):
            f.write(f"Table {i + 1}:\n")
            f.write(table.to_string(index=False))
            f.write("\n\n")

def main(start_url):
    base_url = "{0.scheme}://{0.netloc}".format(requests.utils.urlparse(start_url))
    all_urls = set([start_url])
    visited_urls = set()

    while all_urls - visited_urls:
        url = (all_urls - visited_urls).pop()
        print(f"Visiting: {url}")
        visited_urls.add(url)
        all_urls.update(get_all_links(url, base_url))

    filename = 'extracted_tables.txt'
    if os.path.exists(filename):
        os.remove(filename)

    for url in visited_urls:
        print(f"Extracting tables from: {url}")
        tables = extract_tables_from_url(url)
        save_tables_to_txt(tables, filename)

if __name__ == "__main__":
    start_url = "https://www.pce.ac.in/"  # Replace with the starting URL
    main(start_url)
