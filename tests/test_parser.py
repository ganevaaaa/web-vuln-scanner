from bs4 import BeautifulSoup
from parser import extract_links, extract_forms

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


BASE = "https://example.com/base/"

# --- Tests for extract_links() ---



def test_extract_links_ignores_mailto_and_javascript():
    html = '''
    <a href="mailto:foo@bar.com">Email</a>
    <a href="javascript:void(0)">Do Nothing</a>
    <a href="/contact">Contact</a>
    '''
    soup = BeautifulSoup(html, "html.parser")
    links = extract_links(soup, BASE)
    assert links == ["https://example.com/base/contact"]

def test_extract_links_ignores_empty_and_missing_href():
    html = '''
    <a>No href</a>
    <a href="">Empty</a>
    <a href="/valid">Valid</a>
    '''
    soup = BeautifulSoup(html, "html.parser")
    links = extract_links(soup, BASE)
    assert links == ["https://example.com/base/valid"]

def test_extract_links_strips_fragments():
    html = '''
    <a href="#section">Anchor Only</a>
    <a href="page.html#footer">With Fragment</a>
    '''
    soup = BeautifulSoup(html, "html.parser")
    links = extract_links(soup, "https://example.com/dir/")
    # Expect fragment‐only to be ignored, and fragment‐bearing to be stripped
    assert links == ["https://example.com/dir/page.html"]

# --- Tests for extract_forms() ---

def test_extract_forms_includes_textarea():
    html = '''
    <form action="/comment" method="post">
      <textarea name="comment"></textarea>
      <input type="submit">
    </form>
    '''
    soup = BeautifulSoup(html, "html.parser")
    forms = extract_forms(soup, "https://example.com/page")
    assert len(forms) == 1
    desc = forms[0]
    assert desc["action_url"] == "https://example.com/comment"
    assert desc["method"] == "post"
    assert desc["inputs"] == ["comment"]

def test_extract_forms_no_input_fields():
    html = '''
    <form action="/ping"></form>
    '''
    soup = BeautifulSoup(html, "html.parser")
    forms = extract_forms(soup, "https://example.com/ping")
    assert len(forms) == 1
    desc = forms[0]
    assert desc["action_url"] == "https://example.com/ping"
    assert desc["method"] == "get"   # default
    assert desc["inputs"] == []      # no fields

def test_extract_forms_absolute_action():
    html = '''
    <form action="https://api.example.com/submit" method="GET">
      <input name="q">
    </form>
    '''
    soup = BeautifulSoup(html, "html.parser")
    forms = extract_forms(soup, "https://example.com/home")
    assert len(forms) == 1
    desc = forms[0]
    assert desc["action_url"] == "https://api.example.com/submit"
    assert desc["method"] == "get"
    assert desc["inputs"] == ["q"]

def test_extract_forms_multiple_forms_on_one_page():
    html = '''
    <form action="/one"><input name="a"></form>
    <form action="/two" method="post"><input name="b"></form>
    '''
    soup = BeautifulSoup(html, "html.parser")
    forms = extract_forms(soup, "https://example.com/")
    assert len(forms) == 2

    # first form
    first = forms[0]
    assert first["action_url"] == "https://example.com/one"
    assert first["method"] == "get"
    assert first["inputs"] == ["a"]

    # second form
    second = forms[1]
    assert second["action_url"] == "https://example.com/two"
    assert second["method"] == "post"
    assert second["inputs"] == ["b"]
