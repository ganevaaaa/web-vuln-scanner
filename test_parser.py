import pytest
from bs4 import BeautifulSoup
from parser import extract_forms

# A minimal HTML page with one form, no action, default GET
HTML_NO_ACTION = """
<html><body>
  <form>
    <input name="q">
    <input type="submit">
  </form>
</body></html>
"""

# A form with a relative action and POST method
HTML_RELATIVE = """
<html><body>
  <form action="/login.php" method="POST">
    <input name="user">
    <input name="pass">
  </form>
</body></html>
"""

def test_extract_forms_no_action():
    soup = BeautifulSoup(HTML_NO_ACTION, "html.parser")
    forms = extract_forms(soup, "https://example.com/search")
    assert len(forms) == 1

    desc = forms[0]
    # Since no action, endpoint should be the page URL itself
    assert desc["action_url"] == "https://example.com/search"
    assert desc["method"] == "get"
    assert desc["inputs"] == ["q"]

def test_extract_forms_relative_action():
    soup = BeautifulSoup(HTML_RELATIVE, "html.parser")
    forms = extract_forms(soup, "https://example.com/home")
    assert len(forms) == 1

    desc = forms[0]
    # Relative action resolves against the base page URL
    assert desc["action_url"] == "https://example.com/login.php"
    assert desc["method"] == "post"
    # Only named inputs are collected
    assert set(desc["inputs"]) == {"user", "pass"}

# You can add more tests:
# - multiple forms on one page
# - forms with textarea
# - forms with no inputs
# - absolute action URLs
