# 🔍 Web Vulnerability Scanner 

A lightweight Python-based tool that crawls websites and detects common web vulnerabilities such as **SQL Injection (SQLi)**, **Cross-Site Scripting (XSS)**, and more.

📌 This project is for educational use. It demonstrates how basic web vulnerability scanning works and is not meant to replace professional tools like Burp Suite or OWASP ZAP.


---
## 📌 Project Status

**This project is a work in progress.**

---


## 🚀 Features
- Website crawler using Breadth-First Search (BFS)

- Form detection & parsing (action, method, inputs)

- XSS & SQLi payload injection (GET & POST)

- Reflection & error-based response analysis

- JSON report generation
- CLI argument parsing


🚧 In development:

- Command Injection detection

- HTML report output

- Duplicate finding deduplication / report cleanup
- HTML Report Generation
- Colorized CLI Output
- Scan Summary
- Authenticated Scanning
- Command Injection

- File Inclusion

- Open Redirect

- Missing Security Headers

- Insecure Cookies

---

## 🧠 How It Works

1. **Crawls** the target site and extracts URLs
2. **Finds forms** and input fields on pages
3. **Injects payloads** (from JSON files) into parameters
4. **Analyzes** responses for signs of vulnerabilities
5. **Generates a report** of findings

---

## 📦 Project Structure

## 🛠 Requirements
To install the required Python dependencies, run:
```bash
 pip install -r requirements.txt
```
requests – for making HTTP requests

beautifulsoup4 – for parsing HTML content

pytest – for running unit tests

---
### 🔧 Example Usage

```bash
python main.py --url http://testphp.vulnweb.com --max-pages 20 --i-understand
```

## ⚙️ CLI Arguments
| Argument         | Description                                     |
| ---------------- | ----------------------------------------------- |
| `--url`          | **(required)** The starting URL to scan         |
| `--max-pages`    | Maximum number of pages to crawl   |
| `--i-understand` | Confirms you have permission for non-demo sites |


---
🔐 Ethical Disclaimer
⚠️ For **educational and authorized use only**. Never scan targets you don't have permission to test.
---


Author👩🏻‍💻: Gabriela Ganeva 

GitHub: github.com/ganevaaaa

License: MIT
