import pytest
from datetime import datetime, timedelta
from library_service import calculate_late_fee_for_book

def mock_get_borrow_record_for_patron(patron_id, book_id):
    pass

def test_fee_for_on_time_return(monkeypatch):
    """
    A book returned on its due date, so the late fee should be $0.00
    """
    # Arrange: Simulate a book returned 10 days after borrowing (due in 14 days)
    borrow_date = datetime.now() - timedelta(days=10)
    due_date = borrow_date + timedelta(days=14)
    
    """monkeypatch is used here to mock the fake data to test the function."""
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": due_date}

    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)

    # Act
    result = calculate_late_fee_for_book("222222", 1)

    # Assert
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0

def test_fee_for_5_days_overdue(monkeypatch):
    """
    A book returned 5 days after its due date, so the late fee should be $2.50
    """
    # Arrange: Simulate a book returned 19 days after borrowing (5 days late)
    borrow_date = datetime.now() - timedelta(days=19)
    due_date = borrow_date + timedelta(days=14)

    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}

    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)

    # Act
    result = calculate_late_fee_for_book("222222", 2)

    # Assert
    assert result["fee_amount"] == 2.50  # 5 days * $0.50
    assert result["days_overdue"] == 5

def test_fee_for_10_days_overdue(monkeypatch):
    """
    A book returned 10 days after its due date, so the late fee should be $6.50
    7 days at $0.50 + 3 days at $1.00
    """
    # Arrange: Simulate a book 10 days late
    borrow_date = datetime.now() - timedelta(days=24)
    due_date = borrow_date + timedelta(days=14)

    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}

    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)

    # Act
    result = calculate_late_fee_for_book("222222", 1)

    # Assert
    expected_fee = (7 * 0.50) + (3 * 1.00)  # $3.50 + $3.00 = $6.50
    assert result["fee_amount"] == expected_fee
    assert result["days_overdue"] == 10

def test_fee_is_capped_at_maximum(monkeypatch):
    """
    A book returned 100 days late, so the late fee should be capped at $15.00
    """
    # Arrange: Simulate a book 100 days late
    borrow_date = datetime.now() - timedelta(days=114)
    due_date = borrow_date + timedelta(days=14)

    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}

    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    # Act
    result = calculate_late_fee_for_book("222222", 1)

    # Assert
    assert result["fee_amount"] == 15.00
    assert result["days_overdue"] == 100
