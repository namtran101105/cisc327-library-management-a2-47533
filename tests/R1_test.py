import pytest
from services.library_service import add_book_to_catalog


def test_add_book_valid_input(monkeypatch):
    """Test adding a book with valid input."""
    # Arrange: Simulate that no book with this ISBN exists and the insert will succeed.
    monkeypatch.setattr('services.library_service.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('services.library_service.insert_book', lambda *args: True)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Added 'services.' prefix


    # Act
    success, message = add_book_to_catalog("Oliver Twist", "Charles Dickens", "9780141439741", 5)
    
    # Assert
    assert success is True
    assert "successfully added" in message.lower()


def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short. No database call is expected."""
    # Act
    success, message = add_book_to_catalog("Oliver Twist", "Charles Dickens", "143974", 5)
    
    # Assert
    assert success is False
    assert "13 digits" in message


def test_add_book_with_invalid_number_of_copies():
    """Test adding a book with invalid number of copies. No database call is expected."""
    # Act
    success, message = add_book_to_catalog("Oliver Twist", "Charles Dickens", "9780141439741", -1)
    
    # Assert
    assert success is False
    assert "positive integer" in message


def test_add_book_with_empty_title():
    """Test adding a book with an empty title. No database call is expected."""
    # Act
    success, message = add_book_to_catalog("", "Charles Dickens", "9780141439741", 5)
    
    # Assert
    assert success is False
    assert "title is required" in message.lower()


def test_too_long_title():
    """Test adding a book with a title that is too long. No database call is expected."""
    # Arrange
    long_title = "A" * 201  # 201 characters
    
    # Act
    success, message = add_book_to_catalog(long_title, "Charles Dickens", "9780141439741", 5)
    
    # Assert
    assert success is False
    assert "less than 200 characters" in message.lower()


def test_add_book_with_duplicate_isbn(monkeypatch):
    """Test adding a book with an ISBN that already exists."""
    # Arrange: Simulate that the database finds a book with the given ISBN.
    monkeypatch.setattr('services.library_service.get_book_by_isbn', lambda isbn: {"id": 1, "title": "Existing Book"})
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Added 'services.' prefix


    # Act
    success, message = add_book_to_catalog("New Book", "New Author", "9780141439741", 5)
    
    # Assert
    assert success is False
    assert "already exists" in message.lower()

def test_add_book_author_whitespace_only():
    """Test with author containing only whitespace"""
    success, message = add_book_to_catalog("Valid Title", "   ", "1234567890123", 5)
    assert success is False
    assert "author is required" in message.lower()


def test_add_book_isbn_not_digits():
    """Test ISBN with non-digit characters"""
    success, message = add_book_to_catalog("Title", "Author", "12345X7890123", 5)
    assert success is False
    assert "only digits" in message.lower()


def test_add_book_isbn_wrong_length():
    """Test ISBN with 12 digits instead of 13"""
    success, message = add_book_to_catalog("Title", "Author", "123456789012", 5)
    assert success is False
    assert "13 digits" in message.lower()

def test_add_book_database_insert_fails(monkeypatch):
    """Test when database insert operation fails"""
    monkeypatch.setattr('services.library_service.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('services.library_service.insert_book', lambda *args: False)
    
    success, message = add_book_to_catalog("Title", "Author", "1234567890123", 5)
    assert success is False
    assert "failed" in message.lower() or "error" in message.lower()


def test_add_book_title_with_leading_trailing_spaces(monkeypatch):
    """Test book title with spaces that need trimming"""
    monkeypatch.setattr('services.library_service.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('services.library_service.insert_book', lambda *args: True)
    
    success, message = add_book_to_catalog("  Title  ", "Author", "1234567890123", 5)
    assert success is True


def test_add_book_author_with_leading_trailing_spaces(monkeypatch):
    """Test author name with spaces that need trimming"""
    monkeypatch.setattr('services.library_service.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('services.library_service.insert_book', lambda *args: True)
    
    success, message = add_book_to_catalog("Title", "  Author  ", "1234567890123", 5)
    assert success is True
