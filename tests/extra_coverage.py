"""
Additional tests to reach 80% coverage
"""
import pytest
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron
)


def test_add_book_title_whitespace_only():
    """Test with title containing only spaces"""
    success, msg = add_book_to_catalog("   ", "Author", "1234567890123", 5)
    assert success == False


def test_add_book_author_exceeds_max_length():
    """Test with author name > 100 characters"""
    long_author = "A" * 101
    success, msg = add_book_to_catalog("Title", long_author, "1234567890123", 5)
    assert success == False


def test_borrow_patron_id_contains_letters():
    """Test borrow with patron ID containing letters"""
    success, msg = borrow_book_by_patron("12345A", 1)
    assert success == False


def test_borrow_patron_id_too_long():
    """Test borrow with 7-digit patron ID"""
    success, msg = borrow_book_by_patron("1234567", 1)
    assert success == False


def test_return_patron_id_with_special_chars():
    """Test return with patron ID containing special characters"""
    success, msg = return_book_by_patron("123-45", 1)
    assert success == False

def test_add_book_isbn_with_letters():
    """Test ISBN containing letters"""
    success, msg = add_book_to_catalog("Title", "Author", "123ABC7890123", 5)
    assert success == False


def test_add_book_zero_copies():
    """Test with 0 copies"""
    success, msg = add_book_to_catalog("Title", "Author", "1234567890123", 0)
    assert success == False


def test_borrow_empty_patron_id():
    """Test with empty patron ID"""
    success, msg = borrow_book_by_patron("", 1)
    assert success == False
