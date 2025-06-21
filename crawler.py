"""
    # TODO fix for users

    start_url = "http://testphp.vulnweb.com"
"""
import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time

SLEEP_TIME = 1

MAX_PAGES = 50


class WebCrawler:
    def __init__(self, start_url):
        self.start_url = start_url
        self.visited = set()
        self.queue = deque([start_url])

        # ——————————————
        # robots.txt support
        #Website owners list which parts of the site they don’t want crawled-voluntary
        # convention to be a “good citizen” on the web :)
        domain = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(start_url))
        self.rp = RobotFileParser()
        self.rp.set_url(domain + "/robots.txt")
        self.rp.read()
        self.user_agent = "MyCrawler/1.0"  # can be anything you choose
        # ——————————————

    def start_crawl(self):
        self.visited.clear()
        self.crawl(self.start_url)


    def crawl(self, url):
        self.queue = deque([url])
        self.visited.add(url)

        while self.queue and len(self.visited) < MAX_PAGES:
            current_url = self.queue.popleft()
            print(f"Visiting: {current_url}")
            # robots.txt check
            if not self.rp.can_fetch(self.user_agent, current_url):
                print("Skipped by robots.txt")
                continue
            time.sleep(SLEEP_TIME)
            try:
                # fetch with custom User-Agent
                response = requests.get(current_url,headers={"User-Agent": self.user_agent})

                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                links = self.extract_links(soup, current_url)
                self.is_visited(links)
            except requests.RequestException as e:
                print(f"Failed to fetch {current_url}: {e}")
                continue

    # Because raw HTML is just one big string->use BeautifulSoup

    # soup gives you the tag, but base_url gives you the full path when needed.
    # The browser would know to open the website as rel path , but we need the whole path , thus we
    # reconstruct it using the base url

    def extract_links(self,soup, base_url):
        links = []
        for tag in soup.find_all('a'):
            href = tag.get("href")
            if href:
                # Convert relative URL to full URL
                full_url = urljoin(base_url, href)

                # Keep only internal links (same domain)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    links.append(full_url)

        return links

    def is_visited(self,links):
        for link in links:
            if link not in self.visited:
                self.visited.add(link)
                self.queue.append(link)

        return None

