import json
import requests
from crawler import WebCrawler
from reporting import record_finding,write_report_json


def run_scanner(start_url,max_pages,confirm=False):
    crawler = WebCrawler(start_url)
    crawler.crawl(start_url,max_pages, confirm=confirm)

    for page in crawler.page_forms:
        forms = page["forms"]
        for form in forms:
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
    action_url = form["action_url"]
    method = form["method"].lower()
    input_fields = form["inputs"]
    results = []

    for field in input_fields:
        data = {name: (payload if name == field else '') for name in input_fields}

        try:
            if method == "post":
                response = requests.post(action_url, data=data)
            else:
                response = requests.get(action_url, params=data)

            results.append({
                "url": action_url,
                "method": method,
                "field": field,
                "payload": payload,
                "response": response
            })

        except requests.RequestException as e:
            print(f"[!] Request failed: {e}")
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


