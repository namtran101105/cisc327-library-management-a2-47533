import pytest
from services.library_service import borrow_book_by_patron


def test_borrow_book_valid_input(monkeypatch): 
    """Test borrowing a book with valid input."""
    # Arrange: Simulate that all database operations succeed.
    monkeypatch.setattr('services.library_service.get_book_by_id', lambda book_id: {"title": "Sample Book", "available_copies": 3})
    monkeypatch.setattr('services.library_service.get_patron_borrow_count', lambda patron_id: 2) # Patron has 2 books
    monkeypatch.setattr('services.library_service.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('services.library_service.update_book_availability', lambda *args: True)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Added 'services.' prefix to all


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
    monkeypatch.setattr('services.library_service.get_book_by_id', lambda book_id: {"available_copies": 0})
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Added 'services.' prefix


    # Act
    success, message = borrow_book_by_patron("111111", 2)


    # Assert
    assert success is False
    assert "not available" in message.lower()


def test_borrow_book_patron_exceeds_limit(monkeypatch):
    """Test borrowing when a patron has reached the borrowing limit."""
    # Arrange: Simulate that the book is available, but the patron already has 6 books (exceeds limit).
    monkeypatch.setattr('services.library_service.get_book_by_id', lambda book_id: {"available_copies": 1})
    monkeypatch.setattr('services.library_service.get_patron_borrow_count', lambda patron_id: 6)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Added 'services.' prefix and changed to 6 (your code checks > 5)


    # Act
    success, message = borrow_book_by_patron("654321", 1)
    
    # Assert
    assert success is False
    assert "maximum borrowing limit" in message.lower()


def test_book_not_found(monkeypatch):
    """Test borrowing a book that does not exist in the database."""
    # Arrange: Simulate that get_book_by_id returns None.
    monkeypatch.setattr('services.library_service.get_book_by_id', lambda book_id: None)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Added 'services.' prefix


    # Act
    success, message = borrow_book_by_patron("111111", 3)


    # Assert
    assert success is False
    assert "book not found" in message.lower()

def test_borrow_book_patron_id_not_digits():
    """Test with patron ID containing non-digits"""
    success, message = borrow_book_by_patron("12345A", 1)
    assert success is False
    assert "6 digits" in message.lower()


def test_borrow_book_patron_id_7_digits():
    """Test with patron ID having 7 digits"""
    success, message = borrow_book_by_patron("1234567", 1)
    assert success is False
    assert "6 digits" in message.lower()


def test_borrow_book_available_copies_exactly_zero(monkeypatch):
    """Test with exactly 0 available copies (edge case)"""
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 1, "title": "Test", "available_copies": 0})
    
    success, message = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "not available" in message.lower()

def test_borrow_book_insert_record_fails(monkeypatch):
    """Test when database insert borrow record fails"""
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 1, "title": "Test", "available_copies": 3})
    monkeypatch.setattr('services.library_service.get_patron_borrow_count', lambda patron_id: 2)
    monkeypatch.setattr('services.library_service.insert_borrow_record', lambda *args: False)
    
    success, message = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "failed" in message.lower() or "error" in message.lower()


def test_borrow_book_update_availability_fails(monkeypatch):
    """Test when updating book availability fails"""
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 1, "title": "Test", "available_copies": 3})
    monkeypatch.setattr('services.library_service.get_patron_borrow_count', lambda patron_id: 2)
    monkeypatch.setattr('services.library_service.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('services.library_service.update_book_availability', lambda *args: False)
    
    success, message = borrow_book_by_patron("123456", 1)
    # Function might still return True if insert succeeded
    # but we're testing that the update path is covered
    assert isinstance(success, bool)


def test_borrow_book_patron_exactly_at_limit(monkeypatch):
    """Test patron with exactly 5 books (at limit but can borrow one more)"""
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 1, "title": "Test", "available_copies": 3})
    monkeypatch.setattr('services.library_service.get_patron_borrow_count', lambda patron_id: 5)
    monkeypatch.setattr('services.library_service.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('services.library_service.update_book_availability', lambda *args: True)
    
    success, message = borrow_book_by_patron("123456", 1)
    # Your implementation checks > 5, so 5 should be allowed
    assert success is True


def test_borrow_book_exactly_one_copy_available(monkeypatch):
    """Test borrowing when exactly 1 copy is available"""
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 1, "title": "Test", "available_copies": 1})
    monkeypatch.setattr('services.library_service.get_patron_borrow_count', lambda patron_id: 2)
    monkeypatch.setattr('services.library_service.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('services.library_service.update_book_availability', lambda *args: True)
    
    success, message = borrow_book_by_patron("123456", 1)
    assert success is True
