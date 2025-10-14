import pytest
from library_service import return_book_by_patron

def test_return_book_valid_input(monkeypatch):
    """Test returning a book with valid input."""
    # Arrange: Simulate that the database finds the borrow record and
    # all update operations will be successful.
    borrow_record = {"patron_id": "222222", "book_id": 9780451524935, "return_date": None}
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: borrow_record)
    monkeypatch.setattr('database.update_borrow_record_return_date', lambda pid, bid, rdate: True)
    monkeypatch.setattr('database.update_book_availability', lambda bid, num: True)

    # Act
    success, message = return_book_by_patron("222222", 1)

    # Assert
    assert success is True
    assert "successfully returned" in message.lower()

def test_return_book_not_borrowed_by_patron(monkeypatch):
    """Test returning a book that was not borrowed by the patron."""
    # Arrange: Simulate that the database finds no borrow record for this patron/book pair.
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: None)

    # Act
    success, message = return_book_by_patron("333333", 1)

    # Assert
    assert success is False
    assert "did not borrow this book" in message.lower()

def test_return_already_returned_book(monkeypatch):
    """Test returning a book that has already been returned."""
    # Arrange: Simulate the database returning a record that already has a return date.
    returned_record = {"patron_id": "444444", "book_id": 1, "return_date": "2025-09-20"}
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: returned_record)
    
    # Act
    success, message = return_book_by_patron("444444", 1)

    # Assert
    assert success is False
    assert "already been returned" in message.lower()

def test_return_book_invalid_patron_id():
    """Test returning a book with an invalid patron ID format. No database call expected."""
    # Act
    # Assuming the function validates the patron ID format before any DB calls.
    success, message = return_book_by_patron("12A456", 2)

    # Assert
    assert success is False
    assert "invalid patron id" in message.lower()

def test_return_book_with_invalid_id(monkeypatch):
    """Test returning a book with an ID that does not exist in the catalog."""
    # Arrange: Simulate that the database cannot find the book.
    # When `get_book_by_id` is called with any ID, it will return None.
    monkeypatch.setattr('database.get_book_by_id', lambda book_id: None)

    # Act: Call the function with a valid patron ID but a non-existent book ID.
    success, message = return_book_by_patron("222222", 999)

    # Assert
    assert success is False
    assert "book not found" in message.lower()

def test_return_book_fails_to_update_db(monkeypatch):
    """Test when the return fails during a database update operation."""
    # Arrange: Simulate that the initial check passes, but a subsequent DB write fails.
    borrow_record = {"patron_id": "555555", "book_id": 2, "return_date": None}
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: borrow_record)
    # Simulate the first update succeeding, but the second one failing.
    monkeypatch.setattr('database.update_borrow_record_return_date', lambda pid, bid, rdate: True)
    monkeypatch.setattr('database.update_book_availability', lambda bid, num: False) # This one fails

    # Act
    success, message = return_book_by_patron("555555", 2)

    # Assert
    assert success is False
    assert "database error" in message.lower()
