import pytest
from datetime import datetime, timedelta
from services.library_service import calculate_late_fee_for_book


def test_fee_for_on_time_return(monkeypatch):
    """
    A book returned on its due date, so the late fee should be $0.00
    """
    # Arrange: Patron has an active borrow that's not overdue
    due_date = datetime.now() + timedelta(days=4)  # Due in 4 days (not overdue)
    borrow_date = datetime.now() - timedelta(days=10)
    
    monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
                        lambda patron_id: [{
                            "book_id": 1, 
                            "due_date": due_date,
                            "borrow_date": borrow_date,
                            "return_date": None
                        }])

    # Act
    result = calculate_late_fee_for_book("222222", 1)

    # Assert
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0


# def test_fee_for_5_days_overdue(monkeypatch):
#     """
#     A book 5 days overdue: 5 * $0.50 = $2.50
#     """
#     # Arrange: Book is 5 days overdue
#     due_date = datetime.now() - timedelta(days=5)
#     borrow_date = datetime.now() - timedelta(days=19)  # 14 day loan + 5 overdue
    
#     monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
#                         lambda patron_id: [{
#                             "book_id": 2, 
#                             "due_date": due_date,
#                             "borrow_date": borrow_date,
#                             "return_date": None
#                         }])

#     # Act
#     result = calculate_late_fee_for_book("222222", 2)

#     # Assert
#     assert result["fee_amount"] == 2.50  # 5 days * $0.50
#     assert result["days_overdue"] == 5


# def test_fee_for_7_days_overdue(monkeypatch):
#     """
#     A book 7 days overdue: 7 * $0.50 = $3.50
#     """
#     # Arrange: Book is exactly 7 days overdue
#     due_date = datetime.now() - timedelta(days=7)
#     borrow_date = datetime.now() - timedelta(days=21)
    
#     monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
#                         lambda patron_id: [{
#                             "book_id": 3, 
#                             "due_date": due_date,
#                             "borrow_date": borrow_date,
#                             "return_date": None
#                         }])

#     # Act
#     result = calculate_late_fee_for_book("222222", 3)

#     # Assert
#     assert result["fee_amount"] == 3.50  # 7 days * $0.50
#     assert result["days_overdue"] == 7


# def test_fee_for_10_days_overdue(monkeypatch):
#     """
#     A book 10 days overdue:
#     First 7 days: 7 * $0.50 = $3.50
#     Next 3 days: 3 * $1.00 = $3.00
#     Total: $6.50
#     """
#     # Arrange: Book is 10 days overdue
#     due_date = datetime.now() - timedelta(days=10)
#     borrow_date = datetime.now() - timedelta(days=24)
    
#     monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
#                         lambda patron_id: [{
#                             "book_id": 1, 
#                             "due_date": due_date,
#                             "borrow_date": borrow_date,
#                             "return_date": None
#                         }])

#     # Act
#     result = calculate_late_fee_for_book("222222", 1)

#     # Assert
#     expected_fee = (7 * 0.50) + (3 * 1.00)  # $3.50 + $3.00 = $6.50
#     assert result["fee_amount"] == expected_fee
#     assert result["days_overdue"] == 10


# def test_fee_for_15_days_overdue(monkeypatch):
#     """
#     A book 15 days overdue:
#     First 7 days: 7 * $0.50 = $3.50
#     Next 8 days: 8 * $1.00 = $8.00
#     Total: $11.50
#     """
#     # Arrange: Book is 15 days overdue
#     due_date = datetime.now() - timedelta(days=15)
#     borrow_date = datetime.now() - timedelta(days=29)
    
#     monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
#                         lambda patron_id: [{
#                             "book_id": 5, 
#                             "due_date": due_date,
#                             "borrow_date": borrow_date,
#                             "return_date": None
#                         }])

#     # Act
#     result = calculate_late_fee_for_book("222222", 5)

#     # Assert
#     expected_fee = (7 * 0.50) + (8 * 1.00)  # $3.50 + $8.00 = $11.50
#     assert result["fee_amount"] == expected_fee
#     assert result["days_overdue"] == 15


# def test_fee_is_capped_at_maximum(monkeypatch):
#     """
#     A book 100 days late should be capped at $15.00
#     Without cap: (7 * $0.50) + (93 * $1.00) = $96.50, but capped at $15
#     """
#     # Arrange: Book is 100 days overdue
#     due_date = datetime.now() - timedelta(days=100)
#     borrow_date = datetime.now() - timedelta(days=114)
    
#     monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
#                         lambda patron_id: [{
#                             "book_id": 1, 
#                             "due_date": due_date,
#                             "borrow_date": borrow_date,
#                             "return_date": None
#                         }])
    
#     # Act
#     result = calculate_late_fee_for_book("222222", 1)

#     # Assert
#     assert result["fee_amount"] == 15.00  # Capped at maximum
#     assert result["days_overdue"] == 100


def test_fee_for_no_borrow_record(monkeypatch):
    """
    Test when there's no borrow record at all
    """
    # Arrange: No active records
    monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
                        lambda patron_id: [])
    
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchone(self):
                    return None  # No record found
            return MockResult()
        
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection',
                        lambda: MockConnection())
    
    # Act
    result = calculate_late_fee_for_book("444444", 8)
    
    # Assert
    assert result["status"] == "No borrow record found."
    assert result["fee_amount"] == 0.00


# def test_fee_at_exactly_cap_threshold(monkeypatch):
#     """
#     Test at exactly the point where fee would reach $15.00
#     First 7 days: 7 * $0.50 = $3.50
#     Need $11.50 more to reach $15: 11.5 days at $1.00
#     So 18.5 days total, let's test 19 days
#     """
#     # Arrange: Book is 19 days overdue
#     due_date = datetime.now() - timedelta(days=19)
#     borrow_date = datetime.now() - timedelta(days=33)
    
#     monkeypatch.setattr('services.library_service.get_patron_borrowed_books',
#                         lambda patron_id: [{
#                             "book_id": 9, 
#                             "due_date": due_date,
#                             "borrow_date": borrow_date,
#                             "return_date": None
#                         }])
    
#     # Act
#     result = calculate_late_fee_for_book("222222", 9)
    
#     # Assert
#     expected_fee = (7 * 0.50) + (12 * 1.00)  # $3.50 + $12.00 = $15.50, capped at $15
#     assert result["fee_amount"] == 15.00
#     assert result["days_overdue"] == 19
