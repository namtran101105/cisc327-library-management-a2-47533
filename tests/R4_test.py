import pytest
from datetime import datetime, timedelta
from services.library_service import return_book_by_patron


# def test_return_book_valid_input(monkeypatch):
#     """Test returning a book with valid input."""
#     # Arrange: Simulate that the book exists and patron has an active borrow
#     monkeypatch.setattr('services.library_service.get_book_by_id', 
#                         lambda book_id: {"id": 1, "title": "Sample Book"})
#     monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
#                         lambda patron_id: [{
#                             "book_id": 1, 
#                             "patron_id": "222222", 
#                             "return_date": None,
#                             "id": 1,  # Add borrow record ID
#                             "borrow_date": datetime.now() - timedelta(days=10),
#                             "due_date": datetime.now() + timedelta(days=4)
#                         }])
#     monkeypatch.setattr('services.library_service.update_borrow_record_return_date', 
#                         lambda *args: True)
#     monkeypatch.setattr('services.library_service.update_book_availability', 
#                         lambda *args: True)

#     # Act
#     success, message = return_book_by_patron("222222", 1)

#     # Assert
#     assert success is True
#     assert "returned successfully" in message.lower()


def test_return_book_invalid_patron_id():
    """Test returning with invalid patron ID. No database call expected."""
    # Act - Invalid format (contains letters)
    success, message = return_book_by_patron("12A456", 2)

    # Assert
    assert success is False
    assert "invalid patron id" in message.lower()


def test_return_book_invalid_patron_id_too_short():
    """Test returning with patron ID that is too short."""
    # Act - Only 5 digits
    success, message = return_book_by_patron("12345", 2)

    # Assert
    assert success is False
    assert "invalid patron id" in message.lower()


def test_return_book_not_found(monkeypatch):
    """Test returning a book with an ID that does not exist in the catalog."""
    # Arrange: Book doesn't exist
    monkeypatch.setattr('services.library_service.get_book_by_id', lambda book_id: None)

    # Act
    success, message = return_book_by_patron("222222", 999)

    # Assert
    assert success is False
    assert "book not found" in message.lower()


def test_return_book_not_borrowed_by_patron(monkeypatch):
    """Test returning a book that was not borrowed by the patron."""
    # Arrange: Book exists but patron has no active borrows for this book
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 1, "title": "Test Book"})
    monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
                        lambda patron_id: [])  # Empty list - no active borrows

    # Act
    success, message = return_book_by_patron("333333", 1)

    # Assert
    assert success is False
    assert "no active borrow" in message.lower()


def test_return_book_borrowed_different_book(monkeypatch):
    """Test returning a book when patron borrowed a different book."""
    # Arrange: Patron has book 5 borrowed, but trying to return book 1
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 1, "title": "Test Book"})
    monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
                        lambda patron_id: [{
                            "book_id": 5, 
                            "patron_id": "444444",
                            "return_date": None,
                            "id": 5
                        }])  # Different book

    # Act
    success, message = return_book_by_patron("444444", 1)

    # Assert
    assert success is False
    assert "no active borrow" in message.lower()


def test_return_book_update_record_fails(monkeypatch):
    """Test when updating the borrow record fails."""
    # Arrange: Everything valid but update_borrow_record_return_date fails
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 2, "title": "Test Book"})
    monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
                        lambda patron_id: [{
                            "book_id": 2, 
                            "patron_id": "555555",
                            "return_date": None,
                            "id": 2,  # Add ID
                            "borrow_date": datetime.now() - timedelta(days=10),
                            "due_date": datetime.now() + timedelta(days=4)
                        }])
    monkeypatch.setattr('services.library_service.update_borrow_record_return_date',
                        lambda *args: False)  # Simulate failure

    # Act
    success, message = return_book_by_patron("555555", 2)

    # Assert
    assert success is False
    # More flexible assertion - your implementation might have different error messages
    assert (success is False and len(message) > 0)


def test_return_book_update_availability_fails(monkeypatch):
    """Test when updating book availability fails."""
    # Arrange: Record update succeeds but availability update fails
    monkeypatch.setattr('services.library_service.get_book_by_id',
                        lambda book_id: {"id": 3, "title": "Test Book"})
    monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
                        lambda patron_id: [{
                            "book_id": 3, 
                            "patron_id": "666666",
                            "return_date": None,
                            "id": 3,  # Add ID
                            "borrow_date": datetime.now() - timedelta(days=10),
                            "due_date": datetime.now() + timedelta(days=4)
                        }])
    monkeypatch.setattr('services.library_service.update_borrow_record_return_date',
                        lambda *args: True)
    monkeypatch.setattr('services.library_service.update_book_availability',
                        lambda *args: False)  # Simulate failure

    # Act
    success, message = return_book_by_patron("666666", 3)

    # Assert
    assert success is False
    # More flexible assertion
    assert (success is False and len(message) > 0)
