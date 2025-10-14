import pytest
from library_service import add_book_to_catalog

def test_add_book_valid_input(monkeypatch):
    """Test adding a book with valid input."""
    # Arrange: Simulate that no book with this ISBN exists and the insert will succeed.
    monkeypatch.setattr('database.get_book_by_isbn', lambda isbn: None)
    monkeypatch.setattr('database.insert_book', lambda *args: True)

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
    monkeypatch.setattr('database.get_book_by_isbn', lambda isbn: {"id": 1, "title": "Existing Book"})

    # Act
    success, message = add_book_to_catalog("New Book", "New Author", "9780141439741", 5)
    
    # Assert
    assert success is False
    assert "already exists" in message.lower()

