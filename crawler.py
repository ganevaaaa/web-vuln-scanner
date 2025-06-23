import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import  urlparse
from urllib.robotparser import RobotFileParser
from parser import extract_links, extract_forms
import time
from colorama import Fore, Style, init
import logging

logging.basicConfig(level=logging.INFO)
SLEEP_TIME = 1

init(autoreset=True)


class WebCrawler:
    """
       A web crawler that:
         - Begins at a start URL
         - Follows internal <a href="..."> links in BFS order
         - Respects robots.txt rules
         - Identifies itself via a custom User-Agent
         - Pauses between requests to avoid overloading servers
         - Stops after visiting MAX_PAGES pages
     """
    def __init__(self, start_url):
        """
            Initialize the crawler.
            Args:
            start_url: The first URL to begin crawling from.
        """
        self.start_url = start_url
        self.visited = set()
        self.queue = deque([start_url])
        self.page_forms = []


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
        """
        Clear any previous state and begin crawling from the start_url.
        """
        self.visited.clear()
        self.crawl(self.start_url)

    def crawl(self, url: str, max_pages: int, confirm: bool = False) -> None:
        """
          Perform a BFS crawl starting from the given URL.

          Args:
             url: The URL at which to start (or restart) the crawl.

          Behavior:
           - Resets the queue to begin at `url`
           - Marks `url` as visited
           - Loops until queue is empty or MAX_PAGES reached
           - For each URL:
            * Checks robots.txt via self.rp.can_fetch()
            * Sleeps SLEEP_TIME seconds
            * Sends GET with custom User-Agent
            * Parses HTML for links
            * Enqueues unseen links
        """



        self.queue = deque([url])


        while self.queue and len(self.visited) < max_pages:
            current_url = self.queue.popleft()
            logging.info(f"{Fore.GREEN}Visiting: {current_url}{Style.RESET_ALL}")
            # robots.txt check
            if not self.rp.can_fetch(self.user_agent, current_url):
                logging.warning(f"{Fore.YELLOW}Skipped by robots.txt: {current_url}{Style.RESET_ALL}")
                continue
            time.sleep(SLEEP_TIME)
            try:
                # fetch with custom User-Agent
                response = requests.get(current_url,headers={"User-Agent": self.user_agent})
                self.visited.add(url)

                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                links = extract_links(soup, current_url)
                self.is_visited(links)
                forms = extract_forms(soup, current_url)
                if forms:
                    self.page_forms.append({
                        "page_url": current_url,
                        "forms": forms
                    })
            except requests.RequestException as e:
                print(f"{Fore.RED}Failed to fetch {current_url}: {e}{Style.RESET_ALL}")
                continue



    def is_visited(self,links):
        """
        Add unseen links to the visited set and the crawl queue.

        Args:

        links: A list of URLs extracted from the current page.
        """
        for link in links:
            if link not in self.visited:
                #self.visited.add(link)
                self.queue.append(link)


