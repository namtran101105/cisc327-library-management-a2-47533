import pytest
from library_service import borrow_book_by_patron
from datetime import datetime, timedelta

def test_borrow_book_valid_input(monkeypatch):
    """
    Happy path: Patron successfully borrows an available book.
    """
    monkeypatch.setattr('database.get_book_by_id', 
                       lambda book_id: {"title": "The Great Gatsby", "available_copies": 3})
    monkeypatch.setattr('database.get_patron_borrow_count', lambda patron_id: 2)
    monkeypatch.setattr('database.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('database.update_book_availability', lambda *args: True)
    
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success is True
    assert "successfully borrowed" in message.lower()


def test_borrow_patron_id_too_short():
    """
    Boundary test: Patron ID with 5 digits (one below valid).
    Should be rejected before database access.
    """
    success, message = borrow_book_by_patron("12345", 1)
    
    assert success is False
    assert "6 digits" in message.lower()


def test_borrow_patron_id_too_long():
    """
    Boundary test: Patron ID with 7 digits (one above valid).
    Should be rejected before database access.
    """
    success, message = borrow_book_by_patron("1234567", 1)
    
    assert success is False
    assert "6 digits" in message.lower()


def test_borrow_patron_id_with_letters():
    """
    Invalid input: Non-numeric patron ID should be rejected.
    Tests isdigit() validation.
    """
    success, message = borrow_book_by_patron("12A456", 1)
    
    assert success is False
    assert "6 digits" in message.lower()


def test_borrow_book_not_available(monkeypatch):
    """
    Business rule: Cannot borrow when available_copies = 0.
    """
    monkeypatch.setattr('database.get_book_by_id', 
                       lambda book_id: {"title": "Book", "available_copies": 0})
    
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success is False
    assert "not available" in message.lower()


def test_borrow_exactly_1_available_copy(monkeypatch):
    """
    Boundary test: Last available copy can be borrowed.
    Tests boundary condition available_copies > 0.
    """
    monkeypatch.setattr('database.get_book_by_id', 
                       lambda book_id: {"title": "Last Copy", "available_copies": 1})
    monkeypatch.setattr('database.get_patron_borrow_count', lambda patron_id: 2)
    monkeypatch.setattr('database.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('database.update_book_availability', lambda *args: True)
    
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success is True


def test_borrow_patron_at_limit(monkeypatch):
    """
    Business rule: Patron with > 5 borrows cannot borrow more.
    """
    monkeypatch.setattr('database.get_book_by_id', 
                       lambda book_id: {"title": "Book", "available_copies": 5})
    monkeypatch.setattr('database.get_patron_borrow_count', lambda patron_id: 6)
    
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success is False
    assert "maximum" in message.lower() or "limit" in message.lower()


def test_borrow_patron_exactly_5_books(monkeypatch):
    """
    Boundary test: Patron with exactly 5 books (at limit).
    Based on >5 rejection logic, 5 should be allowed.
    """
    monkeypatch.setattr('database.get_book_by_id', 
                       lambda book_id: {"title": "Book", "available_copies": 3})
    monkeypatch.setattr('database.get_patron_borrow_count', lambda patron_id: 5)
    monkeypatch.setattr('database.insert_borrow_record', lambda *args: True)
    monkeypatch.setattr('database.update_book_availability', lambda *args: True)
    
    success, message = borrow_book_by_patron("123456", 1)
    
    assert success is True


def test_borrow_book_not_found(monkeypatch):
    """
    Edge case: Attempting to borrow non-existent book.
    """
    monkeypatch.setattr('database.get_book_by_id', lambda book_id: None)
    
    success, message = borrow_book_by_patron("123456", 999)
    
    assert success is False
    assert "not found" in message.lower()
