
import scanner

print("⚠️  Use this tool only on websites you own or have permission to test.")
print("⚠️  Unauthorized scanning is illegal.")
MAX_PAGES = 50
start_url= "http://testphp.vulnweb.com" # ← intentionally vulnerable demo site
scanner.run_scanner(start_url, MAX_PAGES)

