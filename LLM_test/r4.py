import pytest
from library_service import return_book_by_patron

def test_return_book_valid_input(monkeypatch):
    """
    Happy path: Patron successfully returns their borrowed book.
    """
    borrow_record = {"patron_id": "222222", "book_id": 1, "return_date": None}
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: borrow_record)
    monkeypatch.setattr('database.update_borrow_record_return_date', lambda *args: True)
    monkeypatch.setattr('database.update_book_availability', lambda *args: True)
    
    success, message = return_book_by_patron("222222", 1)
    
    assert success is True
    assert "successfully returned" in message.lower()


def test_return_book_not_borrowed(monkeypatch):
    """
    Business rule: Cannot return a book not borrowed by this patron.
    """
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: None)
    
    success, message = return_book_by_patron("333333", 1)
    
    assert success is False
    assert "no active borrow" in message.lower()


def test_return_already_returned_book(monkeypatch):
    """
    Business rule: Cannot return a book that's already been returned.
    Tests idempotency and data integrity.
    """
    returned_record = {"patron_id": "444444", "book_id": 1, "return_date": "2025-09-20"}
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: returned_record)
    
    success, message = return_book_by_patron("444444", 1)
    
    assert success is False
    assert "already" in message.lower() and "returned" in message.lower()


def test_return_patron_id_5_digits():
    """
    Boundary test: Patron ID with 5 digits (one below valid).
    Should be rejected during input validation.
    """
    success, message = return_book_by_patron("12345", 1)
    
    assert success is False
    assert "6 digits" in message.lower()


def test_return_patron_id_7_digits():
    """
    Boundary test: Patron ID with 7 digits (one above valid).
    Should be rejected during input validation.
    """
    success, message = return_book_by_patron("1234567", 1)
    
    assert success is False
    assert "6 digits" in message.lower()


def test_return_empty_patron_id():
    """
    Edge case: Empty patron ID string.
    Tests handling of missing required input.
    """
    success, message = return_book_by_patron("", 1)
    
    assert success is False
    assert "invalid patron id" in message.lower()


def test_return_zero_book_id():
    """
    Boundary test: Zero book ID (invalid, minimum is 1).
    Tests positive integer validation for book_id.
    """
    success, message = return_book_by_patron("123456", 0)
    
    assert success is False


def test_return_negative_book_id():
    """
    Invalid input: Negative book ID should be rejected.
    """
    success, message = return_book_by_patron("123456", -1)
    
    assert success is False


def test_return_wrong_patron(monkeypatch):
    """
    Security test: Patron A cannot return Patron B's book.
    Tests ownership validation.
    """
    borrow_record = {"patron_id": "111111", "book_id": 1, "return_date": None}
    monkeypatch.setattr('database.get_borrow_record_for_patron', lambda pid, bid: None)
    
    success, message = return_book_by_patron("222222", 1)
    
    assert success is False
