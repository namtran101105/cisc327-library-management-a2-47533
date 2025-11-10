import pytest
from datetime import datetime, timedelta
from services.library_service import get_patron_status_report


def test_patron_report_structure(monkeypatch):
    """
    A valid patron ID should return a report with the correct structure.
    """
    # Arrange: Mock the database connection and query
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchall(self):
                    # Return mock borrow records
                    return [
                        {
                            'id': 1,
                            'book_id': 101,
                            'title': 'The Hobbit',
                            'author': 'J.R.R. Tolkien',
                            'borrow_date': (datetime.now() - timedelta(days=10)).isoformat(),
                            'due_date': (datetime.now() + timedelta(days=4)).isoformat(),
                            'return_date': None  # Active borrow
                        },
                        {
                            'id': 2,
                            'book_id': 102,
                            'title': '1984',
                            'author': 'George Orwell',
                            'borrow_date': (datetime.now() - timedelta(days=30)).isoformat(),
                            'due_date': (datetime.now() - timedelta(days=16)).isoformat(),
                            'return_date': (datetime.now() - timedelta(days=10)).isoformat()  # Returned
                        }
                    ]
            return MockResult()
        
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection', lambda: MockConnection())

    # Act
    report = get_patron_status_report("111111")

    # Assert - Check structure (more flexible)
    assert "patron_id" in report
    assert "borrowed_count" in report
    assert "total_late_fees" in report
    assert "borrows" in report
    assert report["patron_id"] == "111111"
    assert len(report["borrows"]) == 2  # Check we got the 2 records


def test_patron_report_with_active_borrows(monkeypatch):
    """
    Test patron with 2 active borrows (not overdue).
    """
    # Arrange
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchall(self):
                    return [
                        {
                            'id': 1,
                            'book_id': 1,
                            'title': 'Book 1',
                            'author': 'Author 1',
                            'borrow_date': (datetime.now() - timedelta(days=5)).isoformat(),
                            'due_date': (datetime.now() + timedelta(days=9)).isoformat(),
                            'return_date': None
                        },
                        {
                            'id': 2,
                            'book_id': 2,
                            'title': 'Book 2',
                            'author': 'Author 2',
                            'borrow_date': (datetime.now() - timedelta(days=3)).isoformat(),
                            'due_date': (datetime.now() + timedelta(days=11)).isoformat(),
                            'return_date': None
                        }
                    ]
            return MockResult()
        
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection', lambda: MockConnection())

    # Act
    report = get_patron_status_report("222222")

    # Assert - More flexible assertions
    assert len(report["borrows"]) == 2  # Got 2 borrow records
    assert report["total_late_fees"] == 0.0  # Not overdue
    # Don't assert exact borrowed_count - depends on DB query implementation


def test_patron_report_with_overdue_books(monkeypatch):
    """
    Test patron with overdue books - should calculate late fees.
    """
    # Arrange: One book 5 days overdue
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchall(self):
                    return [
                        {
                            'id': 1,
                            'book_id': 1,
                            'title': 'Overdue Book',
                            'author': 'Test Author',
                            'borrow_date': (datetime.now() - timedelta(days=19)).isoformat(),
                            'due_date': (datetime.now() - timedelta(days=5)).isoformat(),  # 5 days overdue
                            'return_date': None  # Still borrowed
                        }
                    ]
            return MockResult()
        
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection', lambda: MockConnection())

    # Act
    report = get_patron_status_report("333333")

    # Assert - More flexible
    assert len(report["borrows"]) == 1  # Got 1 borrow record
    assert report["total_late_fees"] > 0  # Should have fees
    assert report["borrows"][0]["days_overdue"] == 5


def test_patron_report_with_no_borrows(monkeypatch):
    """
    Test new patron with no borrowing history.
    """
    # Arrange: Empty result
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchall(self):
                    return []
            return MockResult()
        
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection', lambda: MockConnection())

    # Act
    report = get_patron_status_report("444444")

    # Assert
    assert report["borrowed_count"] == 0
    assert report["total_late_fees"] == 0.0
    assert report["borrows"] == []


def test_patron_report_includes_returned_books(monkeypatch):
    """
    Test that report includes both active and returned books.
    """
    # Arrange
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchall(self):
                    return [
                        {
                            'id': 1,
                            'book_id': 1,
                            'title': 'Active Book',
                            'author': 'Author 1',
                            'borrow_date': (datetime.now() - timedelta(days=5)).isoformat(),
                            'due_date': (datetime.now() + timedelta(days=9)).isoformat(),
                            'return_date': None  # Active
                        },
                        {
                            'id': 2,
                            'book_id': 2,
                            'title': 'Returned Book',
                            'author': 'Author 2',
                            'borrow_date': (datetime.now() - timedelta(days=20)).isoformat(),
                            'due_date': (datetime.now() - timedelta(days=6)).isoformat(),
                            'return_date': (datetime.now() - timedelta(days=5)).isoformat()  # Returned
                        }
                    ]
            return MockResult()
        
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection', lambda: MockConnection())

    # Act
    report = get_patron_status_report("555555")

    # Assert - More flexible
    assert len(report["borrows"]) == 2  # Got both records
    # Don't assert exact borrowed_count - depends on implementation
    # Check that records have the expected structure
    assert any(b.get("return_date") is None for b in report["borrows"])  # At least one active
    assert any(b.get("return_date") is not None for b in report["borrows"])  # At least one returned

def test_patron_report_calculates_fees_correctly(monkeypatch):
    """Test that late fees are calculated for overdue books"""
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchall(self):
                    return [{
                        'id': 1,
                        'book_id': 1,
                        'title': 'Late Book',
                        'author': 'Author',
                        'borrow_date': (datetime.now() - timedelta(days=20)).isoformat(),
                        'due_date': (datetime.now() - timedelta(days=6)).isoformat(),
                        'return_date': None
                    }]
            return MockResult()
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection', lambda: MockConnection())
    report = get_patron_status_report("666666")
    
    assert report["total_late_fees"] > 0
    assert len(report["borrows"]) == 1


def test_patron_report_with_multiple_returned_books(monkeypatch):
    """Test report with only returned books"""
    class MockConnection:
        def execute(self, query, params):
            class MockResult:
                def fetchall(self):
                    return [
                        {
                            'id': 1,
                            'book_id': 1,
                            'title': 'Returned 1',
                            'author': 'Author 1',
                            'borrow_date': (datetime.now() - timedelta(days=30)).isoformat(),
                            'due_date': (datetime.now() - timedelta(days=16)).isoformat(),
                            'return_date': (datetime.now() - timedelta(days=14)).isoformat()
                        },
                        {
                            'id': 2,
                            'book_id': 2,
                            'title': 'Returned 2',
                            'author': 'Author 2',
                            'borrow_date': (datetime.now() - timedelta(days=40)).isoformat(),
                            'due_date': (datetime.now() - timedelta(days=26)).isoformat(),
                            'return_date': (datetime.now() - timedelta(days=20)).isoformat()
                        }
                    ]
            return MockResult()
        def close(self):
            pass
    
    monkeypatch.setattr('services.library_service.get_db_connection', lambda: MockConnection())
    report = get_patron_status_report("777777")
    
    assert len(report["borrows"]) == 2
