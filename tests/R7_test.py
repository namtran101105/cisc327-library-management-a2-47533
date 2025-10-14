from library_service import get_patron_status_report
import pytest
from datetime import datetime, timedelta

""""
Fake data for testing
"""

MOCK_BORROWED_BOOKS = [
    {"title": "The Hobbit", "due_date": datetime.now() + timedelta(days=5)},
    {"title": "1984", "due_date": datetime.now() - timedelta(days=3)} 
]

MOCK_BORROWING_HISTORY = [
    {"title": "Fahrenheit 451", "return_date": datetime.now() - timedelta(days=20)}
]

def test_patron_report_structure_and_count(monkeypatch):
    """
    A valid patron ID should return a report with the correct structure and counts.
    """
    # Arrange: Mock all the dependent functions
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: MOCK_BORROWED_BOOKS)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: MOCK_BORROWING_HISTORY)
    # Mock the fee calculation to return a fixed value for this test
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 1.50)

    # Act
    report = get_patron_status_report("111111")

    # Assert
    assert "current_borrowed_books" in report
    assert "borrowing_history" in report
    assert "total_late_fees" in report
    assert "books_currently_borrowed_count" in report
    assert report["books_currently_borrowed_count"] == 2

def test_patron_report_total_late_fees(monkeypatch):
    """
    A valid patron ID should return a report with the correct total late fees.
    """
    # Arrange
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: MOCK_BORROWED_BOOKS)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    # Make the fee calculation return a specific value 
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 5.50)

    # Act
    report = get_patron_status_report("111111")

    # Assert
    assert report["total_late_fees"] == 5.50

def test_patron_report_with_no_current_books(monkeypatch):
    """
    A valid patron ID with no currently borrowed books should return an empty list for current_borrowed_books.
    """
    # Arrange
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: []) # Return empty list
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: MOCK_BORROWING_HISTORY)
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 0.0)

    # Act
    report = get_patron_status_report("123456")

    # Assert
    assert report["current_borrowed_books"] == []
    assert report["books_currently_borrowed_count"] == 0
    assert report["total_late_fees"] == 0.0

def test_patron_report_for_new_patron(monkeypatch):
    """
    A new patron ID with no borrowing history should return empty lists and zero counts.
    """
    # Arrange: All database calls return empty results
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: [])
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 0.0)

    # Act
    report = get_patron_status_report("new_patron")

    # Assert
    assert report["current_borrowed_books"] == []
    assert report["borrowing_history"] == []
    assert report["books_currently_borrowed_count"] == 0
    assert report["total_late_fees"] == 0.0

def test_patron_report_for_invalid_patron_id(monkeypatch):
    """
    An invalid patron ID should raise a ValueError.
    """
    # Arrange: We need to mock the function that validates the patron
    monkeypatch.setattr('database.is_patron_valid', lambda pid: False)

    # Act & Assert
    with pytest.raises(ValueError):
        get_patron_status_report("invalid_id")
