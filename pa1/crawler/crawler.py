
import requests
import hashlib
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

seed_pages = ['https://www.gov.si', 'https://www.evem.gov.si', 'https://www.e-uprava.gov.si', 'https://www.e-prostor.gov.si']
domain = "gov.si"

# Hashes the site source code using MD5 algorithm
def hash(html_site):
    return hashlib.md5(html_site.encode('utf-8')).hexdigest()

# Checks if robots.txt file exists
def robots_file_exists(robots_url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            response = page.goto(robots_url)
            return response.status == 200

    except Exception as e:
        print("has_robots_file exception:", e)
        return False

# Get the contents of robots.txt file
def get_robots_txt(url):
    try:
        response = requests.get(url + "/robots.txt")
        if response.status_code == 200:
            return response.text
        else:
            return "Robots.txt not found or inaccessible."
    except Exception as e:
        return "An error occurred:", str(e)

# Get all sitemaps in the robots.txt file
def get_sitemaps(robots):
    data = []
    lines = str(robots).splitlines()

    for line in lines:
        if line.startswith('Sitemap:'):
            split = line.split(':', maxsplit=1)
            data.append(split[1].strip())
    return data
