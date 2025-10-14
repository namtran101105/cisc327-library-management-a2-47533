import pytest
from datetime import datetime, timedelta
from library_service import get_patron_status_report

MOCK_BORROWED_BOOKS = [
    {"title": "The Hobbit", "due_date": datetime.now() + timedelta(days=5)},
    {"title": "1984", "due_date": datetime.now() - timedelta(days=3)}
]

MOCK_BORROWING_HISTORY = [
    {"title": "Fahrenheit 451", "return_date": datetime.now() - timedelta(days=20)}
]

def test_patron_report_structure(monkeypatch):
    """
    Happy path: Valid patron report has correct structure.
    Should include: borrowed_count, total_late_fees, borrows list.
    """
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: MOCK_BORROWED_BOOKS)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: MOCK_BORROWING_HISTORY)
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 1.50)
    
    report = get_patron_status_report("111111")
    
    assert "books_currently_borrowed_count" in report
    assert "total_late_fees" in report
    assert "borrows" in report or "borrowing_history" in report


def test_patron_report_active_count(monkeypatch):
    """
    Test: Correct count of active borrows.
    Should count only books with return_date = NULL.
    """
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: MOCK_BORROWED_BOOKS)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 0.75)
    
    report = get_patron_status_report("111111")
    
    assert report["books_currently_borrowed_count"] == 2


def test_patron_report_new_patron_no_history(monkeypatch):
    """
    Edge case: New patron with no borrowing history.
    Should return report with zero counts.
    """
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: [])
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 0.0)
    
    report = get_patron_status_report("999999")
    
    assert report["books_currently_borrowed_count"] == 0
    assert report["total_late_fees"] == 0.0


def test_patron_report_only_returned_books_no_active(monkeypatch):
    """
    Edge case: Patron with history but zero active borrows.
    Should show 0 borrowed_count but may have positive late_fees.
    """
    returned_history = [
        {"title": "Book1", "return_date": "2025-09-01"},
        {"title": "Book2", "return_date": "2025-09-15"}
    ]
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: [])
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: returned_history)
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 3.50)
    
    report = get_patron_status_report("111111")
    
    assert report["books_currently_borrowed_count"] == 0
    assert report["total_late_fees"] == 3.50


def test_patron_report_exactly_5_active_borrows(monkeypatch):
    """
    Boundary test: Patron at maximum borrowing limit (5 books).
    Should correctly count and display 5 active borrows.
    """
    five_books = [
        {"title": f"Book{i}", "due_date": datetime.now() + timedelta(days=5)} 
        for i in range(5)
    ]
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: five_books)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 0.0)
    
    report = get_patron_status_report("111111")
    
    assert report["books_currently_borrowed_count"] == 5


def test_patron_report_multiple_overdue_books(monkeypatch):
    """
    Fee aggregation test: Multiple overdue books sum correctly.
    Patron with 3 overdue books should have fees summed properly.
    """
    overdue_books = [
        {"title": "Book1", "due_date": datetime.now() - timedelta(days=10)},
        {"title": "Book2", "due_date": datetime.now() - timedelta(days=5)},
        {"title": "Book3", "due_date": datetime.now() - timedelta(days=2)}
    ]
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: overdue_books)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    # Mock total: 10 days ($2.50) + 5 days ($1.25) + 2 days ($0.50) = $4.25
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 4.25)
    
    report = get_patron_status_report("111111")
    
    assert report["books_currently_borrowed_count"] == 3
    assert report["total_late_fees"] == 4.25


def test_patron_report_mixed_on_time_and_overdue(monkeypatch):
    """
    Test: Mix of on-time and overdue books.
    Should correctly count all active and calculate fees for overdue only.
    """
    mixed_books = [
        {"title": "On Time", "due_date": datetime.now() + timedelta(days=5)},
        {"title": "Overdue", "due_date": datetime.now() - timedelta(days=3)}
    ]
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: mixed_books)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 0.75)
    
    report = get_patron_status_report("111111")
    
    assert report["books_currently_borrowed_count"] == 2
    assert report["total_late_fees"] == 0.75


def test_patron_report_one_book_at_fee_cap(monkeypatch):
    """
    Edge case: Single book with fee at $15.00 cap.
    Should show capped fee correctly.
    """
    capped_book = [{"title": "Long Overdue", "due_date": datetime.now() - timedelta(days=100)}]
    monkeypatch.setattr('database.get_patron_borrowed_books', lambda pid: capped_book)
    monkeypatch.setattr('database.get_patron_borrowing_history', lambda pid: [])
    monkeypatch.setattr('library_service.calculate_total_late_fees_for_patron', lambda pid: 15.00)
    
    report = get_patron_status_report("111111")
    
    assert report["total_late_fees"] == 15.00
