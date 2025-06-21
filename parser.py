from urllib.parse import urljoin, urlparse


# Because raw HTML is just one big string->use BeautifulSoup

# soup gives you the tag, but base_url gives you the full path when needed.
# The browser would know to open the website as rel path , but we need the whole path , thus we
# reconstruct it using the base url
def extract_links(soup, base_url):
    """
    Extract and normalize all internal <a href="..."> links from a parsed page.

    Args:
        soup: BeautifulSoup object of the page HTML.
        base_url: The URL used to resolve relative links.

    Returns:
        A list of fully-qualified URLs on the same domain as base_url.
    """
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


# just like <a href> , a form’s action attribute and <iframe src> point to another URL we  need to know about
# EVERY action is needed to send payloads to teh right  endpoint, they aren't used for crawling itself
# <iframe src> are used for crawling.
def extract_forms(soup, current_url):
    """
      Extract all forms from a page, returning descriptors with:
        - page_url:   the URL where the form was found
        - action_url: fully-resolved endpoint (defaults to current_url if absent)
        - method:     'get' or 'post'
        - inputs:     list of field names
      """
    form_tags = soup.find_all("form")
    forms = []
    for form in form_tags:
        action = form.get("action")
        if not action:
            # When a form has no action specified, browsers default to re-submitting to the same page you’re on.
            endpoint = current_url
        else:
            # Resolve paths->: Servers expect absolute URLs.
            endpoint = urljoin(current_url, action)
            # endpoint holds the exact URL where we  must send the test requests

        # capturing the form’s method ensures the implemented scanner sends payloads exactly as a browser would
        method = form.get("method", "get").lower()

            # By extracting each control’s name, the scanner can place payloads
            # under the exact keys the server looks for—otherwise your tests will silently fail.
        inputs = []
        for control in form.find_all(("input", "textarea")):
            name = control.get("name")
            if name:
                inputs.append(name)
        forms.append({
        "page_url": current_url,
        "action_url": endpoint,
        "method": method,
        "inputs": inputs
        })

    return forms
