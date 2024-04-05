import re
import traceback
import queue
import datetime
import psycopg2
from selenium import webdriver
from urllib import robotparser
from bs4 import BeautifulSoup
from colorama import Style, Fore, init
from tldextract import extract
from selenium.webdriver.chrome.service import Service
import concurrent.futures
import time
import threading
import urllib
import hashlib
import requests

class Frontier:
    
    # We are using queue
    def __init__(self, wait_time = 5):
        self.sites = queue.Queue()
        self.sitesDictionary = {}
        self.numOfPages = 0
        self.wait_time = wait_time

    # Add site
    def add_site(self, domain):
        if(domain in self.sitesDictionary):
            return False

        s = Site(domain)
        self.sites.put(s)
        self.sitesDictionary[domain] = s
        print("Added site ", domain, " to frontier.")
        return True

    # Add page
    def add_page(self, url, domain):
        s = self.sitesDictionary[domain]
        if (s == None):
            return False
        p = Page(url, self.sitesDictionary[domain])
        self.sitesDictionary[domain].add_page(p)
        self.numOfPages += 1
        print("Added page ", url , " to frontier.")
        return True

   # Next url in line
    def get_page(self):
        while(True):
            s = self.sites.get()
            self.sites.put(s)
            if(s.has_page()):
                self.numOfPages -= 1
                page = s.get_page()
                s.halt_till_allowed(self.wait_time)
                s.accessed()
                break
            
        return page

    def has_page(self):
        return self.numOfPages > 0

class Page:

    def __init__(self, u, s):
        self.url = u
        self.site = s

class Site:
    
    def __init__(self, dom):
        self.domain = dom
        self.pages = queue.Queue()
        self.last_accessed = time.time()
        self.numOfPages = 0
	
    def next_allowed_access(self, seconds):
        return (time.time() - self.last_accessed) > seconds

    def accessed(self):
        self.last_accessed = time.time()

    def halt_till_allowed(self, seconds):
        waitTime = self.last_accessed - time.time() + seconds
        if(waitTime > 0):
            time.sleep(waitTime)
        
    def get_page(self):
        self.numOfPages -= 1
        return self.pages.get()

    def add_page(self, p):
        self.pages.put(p)
        self.numOfPages += 1

    def has_page(self):
        return self.numOfPages > 0


# Deletes everything from the database to start over
def reset_database():
    tables = ['image', 'page_data', 'link', 'page', 'site']
    sequences = ['image_id_seq', 'page_data_id_seq', 'page_id_seq', 'site_id_seq']

    for table in tables:
        cur.execute(f"DELETE FROM crawldb.{table} *")

    for seq in sequences:
        cur.execute(f"ALTER SEQUENCE crawldb.{seq} RESTART WITH 1;")

# Does a duplicate page exist? 
def is_a_duplicate(url, html):
	with kljucavnica:
		try:
			cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url,))
			rows = cur.fetchall()
			dolzina = len(rows)
			if dolzina > 1:
				return True
			else:
				hash = html_md5(html)
				cur.execute("SELECT * FROM crawldb.page WHERE content_hash = %s", (hash,))
				rows = cur.fetchall()

				if rows:
					return True
			return False

		except Exception as e:
			print(e)
			return False

# Insert page data to database 
def insert_page_data_to_db(page_data_list):
	with kljucavnica:
		try:
			for page_data in page_data_list:
				page_id = page_data['page_id']
				data_type_code = page_data['data_type_code']
				cur.execute('INSERT INTO crawldb.page_data (page_id, data_type_code) VALUES (%s, %s) RETURNING id;', (page_id, data_type_code))
		except Exception as e:
			print(e)

# Get MD5 hash of the html code 
def html_md5(html):
	return str(hashlib.md5(html.encode('utf-8')).hexdigest())

# Insert image to database 
def insert_imgs_to_db(list_of_images):
	with kljucavnica:
		try:
			for image in list_of_images:
				page_id = image['page_id']
				filename = image['filename']
				content_type = image['content_type']
				cur.execute("INSERT INTO crawldb.image (page_id, filename, content_type, accessed_time) VALUES (%s, %s, %s, NOW());", (page_id, filename, content_type))
		except Exception as e:
			print(e)


# Parse sitemap
def get_urls_from_sitemap(sitemap_content):
    parsed_sitemap = BeautifulSoup(sitemap_content, features="html.parser")
    if parsed_sitemap.find("sitemapindex"):
        for loc in parsed_sitemap.find_all("loc"):
            yield from fetch_sitemap_urls(loc.text)
    elif parsed_sitemap.find("urlset"):
        for url in parsed_sitemap.find_all("url"):
            yield url.text

# Fetch sitemap urls
def fetch_sitemap_urls(sitemap_url):
    request = urllib.request.Request(sitemap_url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request) as response:
        content = response.read().decode("utf-8")
        parsed_sitemap = BeautifulSoup(content, features="html.parser")
        for url in parsed_sitemap.find_all("loc"):
            yield url.text

# Insert URL if it does not exist
def insert_url_if_not_exists(site_id, url, domain):
    cur.execute("SELECT 1 FROM crawldb.page WHERE url = %s LIMIT 1", (url,))
    if not cur.fetchone():
        cur.execute("INSERT INTO crawldb.page(site_id, url) VALUES (%s, %s);", (site_id, url))
        frontier.add_page(url, domain)

# Load sitemap urls to pages
def load_sitemap_urls_to_pages(domain):
    try:
        print(f"Adding sitemap to frontier from domain: {domain}")
        cur.execute("SELECT id, sitemap_content FROM crawldb.site WHERE domain = %s", (domain,))
        site_id, sitemap_content = cur.fetchone()

        for url in get_urls_from_sitemap(sitemap_content):
            insert_url_if_not_exists(site_id, url, domain)

    except Exception as e:
        print(e)


# Are we allowed to crawl? Fetch robots content from the database and check 
def is_allowed_to_crawl(domain, url):
	with kljucavnica:
		try:
			cur.execute("SELECT domain, robots_content FROM crawldb.site WHERE domain = %s", (domain,))
			rows = cur.fetchall()
			rp = urllib.robotparser.RobotFileParser()
			rp.parse(rows[0][1])
			return  rp.can_fetch(USER_AGENT, url)
		except Exception as e:
			return True
		
# Get page id
def get_page_id(url):
	with kljucavnica:
		try:
			cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url,))
			rows = cur.fetchall()
			if rows:
				page_id = rows[0][0]
			return page_id
		except Exception as e:
			print(e)

# Add site to database
def add_site(site):
	with kljucavnica:
		try:
			cur.execute("SELECT * FROM crawldb.site WHERE domain = %s", (site,))
			rows = cur.fetchall()
			if rows:
				site_id = rows[0][0]
			if not rows:
				robots_sitemap_data = get_robots_and_sitemap_data(site)
				cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s) RETURNING id", (site, robots_sitemap_data[0], robots_sitemap_data[1]))
				site_id = cur.fetchone()[0]
				frontier.add_site(site)
			return site_id
		except Exception as e:
			print(e)


# Add page to database
def put_page_in_db(page):
	site_id = page['site_id']
	page_type_code = page['page_type_code']
	url = page['url']
	html_content = page['html_content']
	http_status_code = page['http_status_code']
	content_hash = page['content_hash']
	
	with kljucavnica:
		try:
			cur.execute('SELECT * FROM crawldb.page WHERE url = %s', (url,))
			rows = cur.fetchall()
			if rows:
				page_id = rows[0][0]
			if not rows:
				cur.execute('INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time, content_hash) VALUES (%s, %s, %s, %s, %s, NOW(), %s) RETURNING id', (site_id, page_type_code, url, html_content, http_status_code, content_hash))
				page_id = cur.fetchone()[0]
			return page_id
		except Exception as e:
			print(e)

	

# Create empty page in db
def add_empty_page(page_object):
	site_id = page_object['site_id']
	url = page_object['url']
	#with kljucavnica: # TODO a gre with kljucavnica pred tem zgori al je tko ok, da je po tem?
	with kljucavnica:
		try:
			cur.execute('INSERT INTO crawldb.page (site_id, url) VALUES (%s, %s)', (site_id, url))
		except Exception as e:
			print(e)


# Update page
def update_page_entry(page_id, page_object):
	site_id = page_object['site_id']
	page_type_code = page_object['page_type_code']
	url = page_object['url']
	html_content = page_object['html_content']
	http_status_code = page_object['http_status_code']
	content_hash = page_object['content_hash']
	accessed_time = page_object['accessed_time']
	with kljucavnica:
		try:
			cur.execute('''
                UPDATE crawldb.page
                SET site_id = %s, 
                    page_type_code = %s, 
                    url = %s, 
                    html_content = %s, 
                    http_status_code = %s, 
                    content_hash = %s, 
                    accessed_time = %s
                WHERE id = %s
                ''', (site_id, page_type_code, url, html_content, http_status_code, content_hash, accessed_time, page_id))
			
		except Exception as e:
			print(e)


# Insert link to db
def put_link_in_db(link_object):
	from1 = link_object['from']
	to = link_object['to']
	with kljucavnica:
		try:
			cur.execute('INSERT INTO crawldb.link (from_page, to_page) VALUES (%s, %s)', (from1, to))
		except Exception as e:
			print(e)


# Get url content 
def fetch_url_content(url):
    try:
        request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8")
    except Exception:
        return None

# Get robots.txt and sitemap content 
def get_robots_and_sitemap_data(domain):
    robots_url = f"http://{domain}/robots.txt"
    rp = urllib.robotparser.RobotFileParser(url=robots_url)
    rp.read()

    # Fetch robots.txt content
    robots_data = fetch_url_content(robots_url)

    # Attempt to fetch the first sitemap URL if it exists
    sitemap_url = rp.site_maps()[0] if rp.site_maps() else None
    sitemap_data = fetch_url_content(sitemap_url) if sitemap_url else None

    return (robots_data, sitemap_data)


def set_page_info(id, code, url, cnt, status):
	page = {
		'site_id' : id,
		'page_type_code' : code,
		'url' : url,
		'html_content' : cnt.prettify(),
		'http_status_code' : status,
		'content_hash' : html_md5(cnt),
		'accessed_time' : datetime.datetime.now() 
	}
	
	return page


def check_type(link):
	if ('mailto:' in link) or  ('tel:' in link) or ('javascript:' in link) or (link[0] == '#') or (link == '/'):
		return True
	return False


# Find links hidden in scripts
def find_hidden_links(page_cnt, page_url, links):
	scripts = page_cnt.findAll('script')
	for script in scripts:
		links_from_script = re.findall(r'(http://|https://)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',script.text)
		for link in links_from_script:
			link = ''.join(link)
			if link.startswith('http') == False:
				if check_type(link):
					continue
				if link.startswith('www'):
					link = f'http://{page_url}'.strip()
				elif link.startswith('/'):
					link = f'{page_url}{link}'.strip()
			links.append(link)
	return links

# Find images
def find_images(page_cnt, images):
	imgs = page_cnt.findAll('img')
	for img in imgs:
		if img['src'].startswith('data:image'):
			continue
		images.append(img['src'])
	return images

# Find hyperlinks
def find_hyperlinks(page_cnt, page_url, links):
	hyperlinks = page_cnt.findAll('a')
	for hyperlink in hyperlinks:
		try:
			link = hyperlink['href']
		except Exception as e:
			continue
		if link == '':
			continue
		if not link.startswith('http'):
			if check_type(link):
				continue
			if link.startswith('www'):
				link = f'http://{page_url}'.strip()
			elif link.startswith('/'):
				link = f'{page_url}{link}'.strip()
		links.append(link)
	return links


# Insert image, links, data
def get_images_links(page_url, worker_id):
	
	# absolute path for macOS driver
	# chromedriver_path = '/Users/luka/Downloads/chromedriver-mac-x64/chromedriver'
	
	# Headless chrome browser
	service = Service(executable_path='chromedriver.exe')
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	driver = webdriver.Chrome(service=service, options=options)

	try:
		driver.get(page_url)
	except Exception as e:
		print(f"{Fore.RED} Driver exception! {e} {Style.RESET_ALL}")

	ext = extract(page_url) 
	domain = '.'.join(ext)
	print("Added page ", page_url, "to frontier.")
	print("Added site ", domain, "to frontier.")

	id_current_site = add_site(domain)
	id_current_page = get_page_id(page_url)
	page_content = driver.page_source
	page_cnt = BeautifulSoup(page_content, 'html.parser')

	page_type = get_content_type(page_url, 0)
	page = {}

	# Page type is HTML
	if (page_type['page_type_code'] == 'HTML'):
		page = set_page_info(id_current_site, 'HTML', page_url, page_cnt, page_type['status_code'])
	
	# Page type is not HTML
	elif (page_type['page_type_code'] != 'HTML'):
		page = set_page_info(id_current_site, 'BINARY', page_url, page_cnt, page_type['status_code'])
	
	# Page is a duplicate
	if (is_a_duplicate(page_url, page_cnt) == True):
		page = set_page_info(id_current_site, 'DUPLICATE', page_url, page_cnt, page_type['status_code'])
		update_page_entry(id_current_page, page)
		return
	
	print("Added page ", page_url, " to database.")

	links = []

	# Find images
	images = find_images(page_cnt, [])
	links = find_hidden_links(page_cnt, page_url, links)
	links = find_hyperlinks(page_cnt, page_url, links)


	link_db, page_data = [], []

	# Links prepare
	if (len(links) + 1) > 1:
		links = list(set(links))
		for lenk in links:
			domain_found_link = '.'.join(extract(lenk))
			if (DOMAIN in domain_found_link) and ((page_url+'/' != lenk)):
				page_typ = get_content_type(lenk, 0)
				if (page_typ['page_type_code'] in type_codes.values()) and (page_typ['page_type_code'] != 'HTML'):
					page_data.append({
						'page_id' : id_current_page,
						'data_type_code' : page_typ['page_type_code'],
						'data' : None
					})
					
				if (is_link_in_table_page(lenk) == False):

					if (is_allowed_to_crawl(domain_found_link, lenk)):
						id_site = add_site(domain_found_link) 
						add_empty_page({'site_id':id_site, 'url':lenk})
						frontier.add_page(lenk, domain_found_link)

				link_db.append({ 
					'from': id_current_page, 
					'to': get_page_id(lenk)
				})


	# Image prepare
	image_to_db = []
	if len(images) > 0:
		for img in images:
			filename = img.split('/')[-1].split('.')[0]
			date = datetime.datetime.now()
			image_to_db.append({
				'page_id' : id_current_page,
				'filename' : filename,
				'content_type' : 'img',
				'data' : None,
				'accessed_time' : date
			})

	print("Added data ", page_data, " to page ", page_url)
	driver.close()
	driver.quit()

	# Insert data to database
	insertions(id_current_page, page, image_to_db, page_data, link_db)



# All database insertions 
def insertions(id_current_page, page, image_to_db, page_data, link_db):
	update_page_entry(id_current_page, page)
	insert_imgs_to_db(image_to_db)
	insert_page_data_to_db(page_data)

	for li in link_db:
		put_link_in_db(li)

	return None


# Set page content
def set_page_type(url_link, status_code, type):
	page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': type}
	return page_type


# Get content type
def get_content_type(url_link, status_code):
	res = ''
	page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': 'other'}
	try:
		res = requests.get(url_link)
	except Exception as e:
		print(f"{Fore.RED} Requests error. (get_content_type)\n {e} {Style.RESET_ALL}")
	if res != '':
		try:
			status_code = res.status_code
			content_type = res.headers['Content-Type'].split(';')[0]
		except Exception as e:
			print(f"{Fore.RED} Content type error. (get_content_type)\n {e} {Style.RESET_ALL}")

		if content_type not in type_codes:
			page_type = set_page_type(url_link, status_code, 'other')
		else:
			page_type = set_page_type(url_link, status_code, type_codes[content_type])
	return page_type

# Check if link exists
def is_link_in_table_page(url):
	with kljucavnica:
		cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url,))
		try:
			rows = cur.fetchall()
			if rows:
				print(f"{Fore.LIGHTYELLOW_EX}Url: {url} already exists in the database.{Style.RESET_ALL}")
				return True
			return False
		except Exception as e:
			return False

# Starting multiple threads
def threading_start(id):
	worker_id = str(id)
	print("Starting worker", worker_id)
	while(True):
		if(frontier.has_page()):
			page = frontier.get_page()
			print(f"{Fore.CYAN}Working on: {page.url}{Style.RESET_ALL}")
			try:
				get_images_links(page.url, worker_id)
			except Exception as e:
				track = traceback.format_exc()
				print(f"{Fore.RED}{track}{Style.RESET_ALL}")

			print(f"{Fore.CYAN}Finished working on: {page.url}{Style.RESET_ALL}")
		else:
			print(f"{Fore.RED}Frontier has no more pages, waiting for 30 seconds. {Style.RESET_ALL}")
			time.sleep(30)
			if(not frontier.has_page()):
				break
	print(f"{Fore.RED}{worker_id} No more pages in frontier, shutting worker down. {Style.RESET_ALL}")

# Add original pages to frontier
def add_og_pages():
	page_object = {}
	page_object['url'] = urls[h]
	page_object['site_id'] = site_id
	add_empty_page(page_object)
	frontier.add_site(domains[h])
	frontier.add_page(urls[h], domains[h])

# Frontier object for frontier interaction
frontier = Frontier()

domains = ["gov.si", "evem.gov.si", "e-uprava.gov.si", "e-prostor.gov.si"]
urls = ["https://www.gov.si", "https://evem.gov.si", "https://e-uprava.gov.si", "https://www.e-prostor.gov.si"]

DOMAIN = 'gov.si'

type_codes = {
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : 'DOCX',
	'application/msword' : 'DOC',
	'application/pdf' : 'PDF',
	'application/vnd.openxmlformats-officedocument.presentationml.presentation' : 'PPTX',
	'text/html' : 'HTML',
	'application/vnd.ms-powerpoint' : 'PPT',
}

# absolute path for macOS driver
# chromedriver_path = '/Users/luka/Downloads/chromedriver-mac-x64/chromedriver'

kljucavnica = threading.Lock()
service = Service(executable_path='chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(service=service, options=options)

connection_details = "host=localhost dbname=user user=user password=SecretPassword"
conn = psycopg2.connect(connection_details)
conn.autocommit = True

request_rate_sec = 4
USER_AGENT = "fri-ieps-R"

cur = conn.cursor()

# Reset database
reset_database()

for h in range(len(urls)):
	site_id = add_site(domains[h])
	add_og_pages()

# Select number of workers
worker_count = 16

with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
	print("\n --- executing ",worker_count," workers ---\n")
	for i in range(worker_count):
		executor.submit(threading_start, i)
		time.sleep(10)