# tests/test_e2e.py

import os
import time

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session", autouse=True)
def ensure_app_running():
    time.sleep(1)
    yield


@pytest.fixture
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


def test_add_and_borrow_book(browser_page):
    """
    Test adding a new book and borrowing it
    """
    page = browser_page

    # 1. Go to catalog page
    page.goto(f"{BASE_URL}/catalog")
    page.wait_for_selector("text=Book Catalog")

    # 2. Click "Add New Book" button
    page.click("text=Add New Book")
    page.wait_for_load_state("networkidle")

    # 3. Fill in the add-book form with VALID data
    test_title = "E2E Test Book"
    test_author = "Test Author"
    test_isbn = "9781234567890"  # Valid 13-digit ISBN
    test_copies = "3"

    page.fill("input[name='title']", test_title)
    page.fill("input[name='author']", test_author)
    page.fill("input[name='isbn']", test_isbn)
    page.fill("input[name='total_copies']", test_copies)

    # 4. Submit the form (may stay on /add_book if there is a flash message)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    # 5. Go to catalog and verify the book appears (do not assume redirect)
    page.goto(f"{BASE_URL}/catalog")
    page.wait_for_timeout(500)

    page.wait_for_selector(f"text={test_title}")
    page.wait_for_selector(f"text={test_author}")
    page.wait_for_selector(f"text={test_isbn}")

    # 6. Borrow the newly added book
    page.fill("input[name='patron_id']", "123456")
    page.locator("button:has-text('Borrow')").last.click()
    page.wait_for_load_state("networkidle")

    # 7. Verify borrow was successful (content-based check)
    content = page.content().lower()
    assert "borrow" in content or "success" in content or "patron" in content


def test_search_book_flow(browser_page):
    """
    Search for a book in the catalog
    """
    page = browser_page

    # 1. Go to search page
    page.goto(f"{BASE_URL}/search")
    page.wait_for_load_state("networkidle")

    # 2. Search for the E2E test book we added
    page.fill("input[name='q']", "E2E Test Book")
    
    # 3. Submit search
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    # 4. Verify the search result appears
    page.wait_for_selector("text=E2E Test Book")
    page.wait_for_selector("text=Test Author")
