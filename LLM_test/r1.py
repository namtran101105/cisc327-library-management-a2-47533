import pytest
from library_service import add_book_to_catalog

def test_add_book_valid_input(monkeypatch):
    """
    Happy path: Add a book with all valid inputs.
    Verifies successful catalog addition with proper message.
    """
    monkeypatch.setattr('database.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('database.insert_book', lambda *args: True)
    
    success, message = add_book_to_catalog("1984", "George Orwell", "9780451524935", 5)
    
    assert success is True
    assert "successfully added" in message.lower()


def test_add_book_isbn_with_letters(monkeypatch):
    """
    Invalid input: ISBN containing letters should be rejected.
    Tests the all-digit validation added to fix Assignment 1 bug.
    """
    success, message = add_book_to_catalog("Book Title", "Author Name", "978014143974A", 5)
    
    assert success is False
    assert "only digits" in message.lower()


def test_add_book_title_exactly_200_chars(monkeypatch):
    """
    Boundary test: Title at exact maximum length (200 characters).
    Should be accepted as valid.
    """
    monkeypatch.setattr('database.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('database.insert_book', lambda *args: True)
    title = "A" * 200
    
    success, message = add_book_to_catalog(title, "Author", "9780451524935", 5)
    
    assert success is True


def test_add_book_title_201_chars(monkeypatch):
    """
    Boundary test: Title exceeding limit by 1 character.
    Should be rejected.
    """
    title = "B" * 201
    
    success, message = add_book_to_catalog(title, "Author", "9780451524935", 5)
    
    assert success is False
    assert "200 characters" in message.lower()


def test_add_book_author_exactly_100_chars(monkeypatch):
    """
    Boundary test: Author at exact maximum length (100 characters).
    Should be accepted as valid.
    """
    monkeypatch.setattr('database.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('database.insert_book', lambda *args: True)
    author = "C" * 100
    
    success, message = add_book_to_catalog("Title", author, "9780451524935", 5)
    
    assert success is True


def test_add_book_empty_title():
    """
    Invalid input: Empty title should be rejected.
    Tests required field validation.
    """
    success, message = add_book_to_catalog("", "Author", "9780451524935", 5)
    
    assert success is False
    assert "title is required" in message.lower()


def test_add_book_whitespace_only_title():
    """
    Edge case: Whitespace-only title should be treated as empty.
    Tests .strip() validation logic.
    """
    success, message = add_book_to_catalog("   ", "Author", "9780451524935", 5)
    
    assert success is False
    assert "title is required" in message.lower()


def test_add_book_isbn_too_short():
    """
    Boundary test: ISBN with 12 digits (one below valid length).
    Should be rejected.
    """
    success, message = add_book_to_catalog("Title", "Author", "978045152493", 5)
    
    assert success is False
    assert "13 digits" in message.lower()


def test_add_book_isbn_too_long():
    """
    Boundary test: ISBN with 14 digits (one above valid length).
    Should be rejected.
    """
    success, message = add_book_to_catalog("Title", "Author", "97804515249351", 5)
    
    assert success is False
    assert "13 digits" in message.lower()


def test_add_book_zero_copies():
    """
    Boundary test: Zero copies is invalid (minimum is 1).
    Tests positive integer validation.
    """
    success, message = add_book_to_catalog("Title", "Author", "9780451524935", 0)
    
    assert success is False
    assert "positive integer" in message.lower()


def test_add_book_negative_copies():
    """
    Invalid input: Negative copies should be rejected.
    """
    success, message = add_book_to_catalog("Title", "Author", "9780451524935", -3)
    
    assert success is False
    assert "positive integer" in message.lower()


def test_add_book_duplicate_isbn(monkeypatch):
    """
    Business rule: Cannot add book with duplicate ISBN.
    Tests unique constraint enforcement.
    """
    existing_book = {"id": 1, "title": "Existing", "isbn": "9780451524935"}
    monkeypatch.setattr('database.get_book_by_isbn', lambda isbn: existing_book)
    
    success, message = add_book_to_catalog("New Book", "Author", "9780451524935", 5)
    
    assert success is False
    assert "already exists" in message.lower()
