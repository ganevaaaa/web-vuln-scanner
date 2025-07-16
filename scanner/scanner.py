import json
from crawler import WebCrawler
from reporting import record_finding, write_report_json
import os
import logging
import requests

def run_scanner(start_url, max_pages, confirm=False):
    """
       Run the full web vulnerability scanner.

       This function launches the WebCrawler, collects all forms from crawled pages,
       and tests each form for common web vulnerabilities including:
         - Missing CSRF token in POST forms
         - Reflected XSS
         - SQL Injection

       Args:
           start_url (str): The starting URL to begin crawling from.
           max_pages (int): The maximum number of pages to crawl.
           confirm (bool): Whether to ignore robots.txt rules (default is False).

       Behavior:
           - Crawls the website and collects forms
           - For each form:
               - Detects and logs missing CSRF protection
               - Injects all payloads into each field
               - Analyzes server responses for signs of vulnerabilities
           - Writes findings to a structured report (JSON)
       """
    crawler = WebCrawler(start_url)
    crawler.start_crawl(max_pages, confirm=confirm)

    for page in crawler.page_forms:
        forms = page["forms"]
        for form in forms:

            # checks if CSRF token is missing ; CSRF is only relevant for POST forms.
            if form["method"] == "post" and not form.get("has_csrf_token"):
                record_finding(
                    page["page_url"],
                    form["action_url"],
                    "-",
                    "-",
                    "csrf",
                    "Missing CSRF token"
                )

            for payload in load_payloads():
                results = inject_form(form, payload)
                for res in results:
                    analyze_response(
                        res["response"],
                        res["field"],
                        res["payload"],
                        form,
                        page["page_url"]
                    )

    write_report_json()





def inject_form(form, payload):
    """
    Inject a payload into a web form, one field at a time.

    For each input field in the given form, this function:
        - Sends a request with the payload injected into that field
        - Preserves CSRF-like tokens to avoid request rejections
        - Mimics a browser using headers
        - Collects the server's response for analysis

    Args:
        form (dict): A dictionary containing:
            - action_url (str): Where to send the form data
            - method (str): HTTP method ('get' or 'post')
            - inputs (list): List of input field dictionaries with names and types
        payload (str): The malicious payload to inject

    Returns:
        List[dict]: A list of results, each containing:
            - url (str): The form's action URL
            - method (str): HTTP method used
            - field (str): The name of the field injected
            - payload (str): The injected payload
            - response (requests.Response): The server's response object
    """
    action_url = form["action_url"]
    method = form["method"].lower()
    input_fields = form["inputs"]
    results = []

    token_keywords = ["csrf", "token", "auth", "verify", "nonce"]

    # loop through inputs
    for field_def in input_fields:
        field_name = field_def["name"]  # get their names
        data = {}

        for f in input_fields:
            name = f["name"]
            # if input is token - leaves it to avoid request rejections.
            if any(k in name.lower() for k in token_keywords):
                data[name] = f.get("value", "")
            else:
                data[name] = payload if name == field_name else ""

        # Set headers to MIMIC browser and bypass basic CSRF protection
        headers = {
            "User-Agent": "TheBestScanner/1.0",
            "X-Requested-With": "XMLHttpRequest"  # makes the request look  like it's from JavaScript,
            # because  many CSRF protections look for this.
        }

        # Add CSRF token to header if present in form; already kept in the form but puts it in the
        # header just in case the framework expects that too/eg. Django, Rails/
        for f in input_fields:
            name = f["name"]
            if any(k in name.lower() for k in token_keywords):
                headers["X-CSRF-Token"] = f.get("value", "")
                break

        try:
            # Sending the requests with the corresponding methods
            # Sends data with the payload
            if method == "post":
                response = requests.post(action_url, data=data, headers=headers)
            else:
                response = requests.get(action_url, params=data, headers=headers)

            logging.info(f"Injected into '{field_name}' on {action_url} → Status {response.status_code}")

            results.append({
                "url": action_url,
                "method": method,
                "field": field_name,
                "payload": payload,
                "response": response
            })

        except requests.RequestException as e:
            logging.error(f"[!] Request failed for field '{field_name}': {e}")
            continue

    return results


def analyze_response(response, field, payload, form, page_url):
    text = response.text.lower()

    if payload.lower() in text:
        print(f"[XSS] Payload reflected in response → field: {field} | payload: {payload}")
        record_finding(page_url, form["action_url"], field, payload, "xss", "payload reflected in HTML")

    sql_errors = [
        "you have an error in your sql syntax",
        "warning: mysql",
        "unclosed quotation mark",
        "quoted string not properly terminated"
    ]
    if any(error in text for error in sql_errors):
        print(f"[SQLi] Error message detected → field: {field} | payload: {payload}")
        record_finding(page_url, form["action_url"], field, payload, "sqli", "SQL error string detected")


def load_payloads():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(base_dir, "..", "payloads")

    with open(os.path.join(payload_path, "xss.json")) as f:
        xss_payloads = json.load(f)
    with open(os.path.join(payload_path, "sqli.json")) as f:
        sqli_payloads = json.load(f)

    return xss_payloads + sqli_payloads
