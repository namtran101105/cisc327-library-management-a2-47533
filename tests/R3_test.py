import pytest
from library_service import borrow_book_by_patron

def test_borrow_book_valid_input(monkeypatch): 
    """Test borrowing a book with valid input."""
    # Arrange: Simulate that all database operations succeed.
    monkeypatch.setattr('database.get_book_by_id', lambda book_id: {"title": "Sample Book", "available_copies": 3})
    monkeypatch.setattr('database.get_patron_borrow_count', lambda patron_id: 2) # Patron has 2 books
    monkeypatch.setattr('database.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('database.update_book_availability', lambda *args: True)

    # Act
    success, message = borrow_book_by_patron("123456", 1)
    
    # Assert
    assert success is True
    assert "successfully borrowed" in message.lower()

def test_borrow_book_invalid_patron_id_too_short():
    """Test borrowing with a patron ID that is too short. No database call expected."""
    # Act
    success, message = borrow_book_by_patron("123", 2)

    # Assert
    assert success is False
    assert "6 digits" in message.lower()

def test_borrow_no_copies_available(monkeypatch):
    """Test borrowing a book with no available copies."""
    # Arrange: Simulate that the database returns a book with 0 available copies.
    monkeypatch.setattr('database.get_book_by_id', lambda book_id: {"available_copies": 0})

    # Act
    success, message = borrow_book_by_patron("111111", 2)

    # Assert
    assert success is False
    assert "not available" in message.lower()

def test_borrow_book_patron_exceeds_limit(monkeypatch):
    """Test borrowing when a patron has reached the borrowing limit."""
    # Arrange: Simulate that the book is available, but the patron already has 5 books.
    monkeypatch.setattr('database.get_book_by_id', lambda book_id: {"available_copies": 1})
    monkeypatch.setattr('database.get_patron_borrow_count', lambda patron_id: 5)

    # Act
    success, message = borrow_book_by_patron("654321", 1)
    
    # Assert
    assert success is False
    assert "maximum borrowing limit" in message.lower()

def test_book_not_found(monkeypatch):
    """Test borrowing a book that does not exist in the database."""
    # Arrange: Simulate that get_book_by_id returns None.
    monkeypatch.setattr('database.get_book_by_id', lambda book_id: None)

    # Act
    success, message = borrow_book_by_patron("111111", 3)

    # Assert
    assert success is False
    assert "book not found" in message.lower()

def test_already_borrowed_book(monkeypatch):
    """Test borrowing a book that the patron has already borrowed.
    Assumes their is a function `database.has_patron_borrowed_book` to check this."""

    # Arrange: Simulate that the book is available and patron has not exceeded limit,
    monkeypatch.setattr('database.get_book_by_id', lambda book_id: {"available_copies": 1})
    monkeypatch.setattr('database.get_patron_borrow_count', lambda patron_id: 2)
    monkeypatch.setattr('database.has_patron_borrowed_book', lambda patron_id, book_id: True)

    # Act
    success, message = borrow_book_by_patron("111111", 4)

    # Assert
    assert success is False
    assert "already borrowed" in message.lower()

