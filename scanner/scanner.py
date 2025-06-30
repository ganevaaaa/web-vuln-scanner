import json
import requests
from crawler import WebCrawler
from reporting import record_finding,write_report_json


def run_scanner(start_url,max_pages,confirm=False):
    crawler = WebCrawler(start_url)
    crawler.start_crawl(max_pages, confirm=confirm)

    for page in crawler.page_forms:
        forms = page["forms"]
        for form in forms:
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


import logging
import requests

def inject_form(form, payload):
    action_url = form["action_url"]
    method = form["method"].lower()
    input_fields = form["inputs"]
    results = []

    token_keywords = ["csrf", "token", "auth", "verify", "nonce"]

    for field_def in input_fields:
        field_name = field_def["name"]
        data = {}

        for f in input_fields:
            name = f["name"]
            if any(k in name.lower() for k in token_keywords):
                data[name] = f.get("value", "")  # Preserve CSRF-like tokens
            else:
                data[name] = payload if name == field_name else ""

        # Set headers to mimic browser and bypass basic CSRF protection
        headers = {
            "User-Agent": "Scanner/1.0",
            "X-Requested-With": "XMLHttpRequest"
        }

        # Add CSRF token to header if present in form
        for f in input_fields:
            name = f["name"]
            if any(k in name.lower() for k in token_keywords):
                headers["X-CSRF-Token"] = f.get("value", "")
                break

        try:
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
    with open('../payloads/xss.json') as f:
        xss_payloads = json.load(f)
    with open('../payloads/sqli.json') as f:
        sqli_payloads = json.load(f)
    return xss_payloads + sqli_payloads


