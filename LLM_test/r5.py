import pytest
from datetime import datetime, timedelta
from library_service import calculate_late_fee_for_book

def test_fee_on_time_return(monkeypatch):
    """
    Happy path: Book returned on due date, no late fee.
    """
    borrow_date = datetime.now() - timedelta(days=10)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": due_date}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0


def test_fee_1_day_overdue(monkeypatch):
    """
    Boundary test: Minimum overdue (1 day) in first tier.
    Fee = 1 × $0.25 = $0.25
    """
    borrow_date = datetime.now() - timedelta(days=15)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["fee_amount"] == 0.25
    assert result["days_overdue"] == 1


def test_fee_exactly_7_days_overdue(monkeypatch):
    """
    CRITICAL boundary: Last day of first tier.
    Fee = 7 × $0.25 = $1.75
    Tests upper boundary of first tier rate.
    """
    borrow_date = datetime.now() - timedelta(days=21)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["fee_amount"] == 1.75  # 7 * 0.25
    assert result["days_overdue"] == 7


def test_fee_exactly_8_days_overdue(monkeypatch):
    """
    CRITICAL boundary: First day of second tier (tier transition).
    Fee = (7 × $0.25) + (1 × $0.50) = $1.75 + $0.50 = $2.25
    Tests correct implementation of two-tier rate system.
    """
    borrow_date = datetime.now() - timedelta(days=22)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    expected_fee = (7 * 0.25) + (1 * 0.50)
    assert result["fee_amount"] == expected_fee
    assert result["days_overdue"] == 8


def test_fee_10_days_overdue(monkeypatch):
    """
    Test: 10 days overdue spans both tiers.
    Fee = (7 × $0.25) + (3 × $0.50) = $1.75 + $1.50 = $3.25
    """
    borrow_date = datetime.now() - timedelta(days=24)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["fee_amount"] == 3.25
    assert result["days_overdue"] == 10


def test_fee_at_cap_15_dollars(monkeypatch):
    """
    Boundary test: Fee reaches $15.00 cap.
    At 38+ days overdue, calculated fee exceeds cap and is capped.
    Fee = (7 × $0.25) + (31 × $0.50) = $17.25, capped to $15.00
    """
    borrow_date = datetime.now() - timedelta(days=52)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": datetime.now()}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["fee_amount"] == 15.00
    assert result["days_overdue"] == 38


def test_fee_no_return_date_currently_overdue(monkeypatch):
    """
    Edge case: Active borrow (return_date = NULL) that is overdue.
    Should calculate fees against today's date.
    Simulates checking current fees for unreturned overdue books.
    """
    borrow_date = datetime.now() - timedelta(days=20)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": None}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["days_overdue"] == 6
    assert result["fee_amount"] == 1.50  # 6 * 0.25


def test_fee_no_return_date_not_yet_overdue(monkeypatch):
    """
    Edge case: Active borrow not yet overdue (still within 14 days).
    Should show $0.00 fee.
    """
    borrow_date = datetime.now() - timedelta(days=7)
    due_date = borrow_date + timedelta(days=14)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": None}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0


def test_fee_returned_early(monkeypatch):
    """
    Edge case: Book returned before due date.
    Should have zero fee and negative/zero overdue days.
    """
    borrow_date = datetime.now() - timedelta(days=10)
    due_date = borrow_date + timedelta(days=14)
    return_date = due_date - timedelta(days=2)
    
    def mock_db_call(patron_id, book_id):
        return {"borrow_date": borrow_date, "due_date": due_date, "return_date": return_date}
    
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', mock_db_call)
    
    result = calculate_late_fee_for_book("222222", 1)
    
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0


def test_fee_no_borrow_record(monkeypatch):
    """
    Edge case: No borrow record exists for patron/book pair.
    Should return zero fee with appropriate status message.
    """
    monkeypatch.setattr('library_service.get_borrow_record_for_patron', lambda pid, bid: None)
    
    result = calculate_late_fee_for_book("999999", 999)
    
    assert result["fee_amount"] == 0.00
    assert "no borrow record" in result["status"].lower()
