import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from parser import extract_links, extract_forms
import time
from colorama import Fore, Style, init
import logging

logging.basicConfig(level=logging.INFO)

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
    SLEEP_TIME = 1

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
        # Website owners list which parts of the site they don’t want crawled-voluntary
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

        self.queue = deque([url])
        while self.queue and len(self.visited) < max_pages:
            current_url = self.queue.popleft()
            if not self.should_visit(current_url, confirm):
                continue
            html = self.fetch_page(current_url)
            if not html:
                continue
            self.extract_links_and_forms(html, current_url)






    def should_visit(self, url, confirm: bool) -> bool:
        """
           Determine whether the given URL should be visited.

           Args:
               url (str): The URL to evaluate.
               confirm (bool): Whether to override robots.txt restrictions.

           Returns:
               bool: True if the URL should be visited; False otherwise.

           Behavior:
               - Skips URLs that have already been visited.
               - Skips URLs disallowed by robots.txt unless confirm=True.
           """
        if url in self.visited:
            return False
        if not confirm and not self.rp.can_fetch(self.user_agent, url):
            logging.warning(f"{Fore.YELLOW}Skipped by robots.txt: {url}{Style.RESET_ALL}")
            return False
        return True

    def fetch_page(self, url):
        """
        Send a GET request to the specified URL and return the HTML content.

        Args:
            url (str): The URL to fetch.

        Returns:
            str or None: The HTML content of the page, or None on failure.

        Behavior:
            - Logs the request.
            - Waits SLEEP_TIME seconds before sending the request.
            - Uses a custom User-Agent.
            - Marks the URL as visited if the request is successful.
        """
        logging.info(f"{Fore.GREEN}Visiting: {url}{Style.RESET_ALL}")
        time.sleep(self.SLEEP_TIME)
        try:
            response = requests.get(url, headers={"User-Agent": self.user_agent})
            self.visited.add(url)
            return response.text
        except requests.RequestException as e:
            logging.error(f"{Fore.RED}Failed to fetch {url}: {e}{Style.RESET_ALL}")
            return None

    def extract_links_and_forms(self, html, current_url):
        """
            Parse HTML content and extract all internal links and forms.

            Args:
                html (str): The HTML content of the current page.
                current_url (str): The URL of the page being processed.

            Behavior:
                - Extracts <a> links and adds new ones to the crawl queue.
                - Extracts <form> tags and stores their metadata in page_forms.
            """
        soup = BeautifulSoup(html, "html.parser")
        links = extract_links(soup, current_url)
        self.enqueue_unvisited_links(links)

        forms = extract_forms(soup, current_url)
        if forms:
            self.page_forms.append({
                "page_url": current_url,
                "forms": forms
            })

    def enqueue_unvisited_links(self, links):
        """
        Add unseen links to the visited set and the crawl queue.

        Args:

        links: A list of URLs extracted from the current page.
        """
        for link in links:
            if link not in self.visited:
                # self.visited.add(link)
                self.queue.append(link)
