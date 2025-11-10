import pytest
from services.library_service import search_books_in_catalog


MOCK_CATALOG = [
    {
        "id": 11111, 
        "title": "Harry Potter and the Sorcerer's Stone", 
        "author": "J.K. Rowling", 
        "isbn": "9780590353427"
    },
    {
        "id": 22222, 
        "title": "The Hobbit", 
        "author": "J.R.R. Tolkien", 
        "isbn": "9780618260300"
    },
    {
        "id": 33333, 
        "title": "Harry Potter and the Chamber of Secrets", 
        "author": "J.K. Rowling", 
        "isbn": "9780439064873"
    }
]


def test_search_by_title_partial(monkeypatch):
    """
    Typing the name "Harry" by the type "title", the function should return 
    2 books with "Harry" in the title.
    """
    # Arrange
    monkeypatch.setattr('services.library_service.get_all_books', lambda: MOCK_CATALOG)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Changed to correct function name with prefix

    # Act
    results = search_books_in_catalog("harry", "title")

    # Assert
    assert len(results) == 2
    assert results[0]["title"] == "Harry Potter and the Sorcerer's Stone"
    assert results[1]["title"] == "Harry Potter and the Chamber of Secrets"


def test_search_by_author_partial(monkeypatch):
    """
    Typing the name "Rowling" by the type "author", the function should return
    2 books with "Rowling" in the author.
    """
    # Arrange
    monkeypatch.setattr('services.library_service.get_all_books', lambda: MOCK_CATALOG)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Changed to correct function name with prefix

    # Act
    results = search_books_in_catalog("rowling", "author")

    # Assert
    assert len(results) == 2
    assert results[0]["author"] == "J.K. Rowling"
    assert results[1]["author"] == "J.K. Rowling"


def test_search_by_isbn_exact_match(monkeypatch):
    """
    Typing the exact ISBN "9780618260300" by the type "isbn", the function should return
    1 book with that exact ISBN.
    """
    # Arrange
    monkeypatch.setattr('services.library_service.get_book_by_isbn', 
                        lambda isbn: MOCK_CATALOG[1] if isbn == "9780618260300" else None)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: ISBN search uses get_book_by_isbn, not get_all_books
    search_isbn = "9780618260300"

    # Act
    results = search_books_in_catalog(search_isbn, "isbn")

    # Assert
    assert len(results) == 1
    assert results[0]["title"] == "The Hobbit"


def test_search_with_no_results(monkeypatch):
    """
    Enter a non-existent title, the function should return an empty list.
    """
    # Arrange
    monkeypatch.setattr('services.library_service.get_all_books', lambda: MOCK_CATALOG)
    # ^^^^^^^^^^^^^^^^^^^^ UPDATED: Added correct prefix

    # Act
    results = search_books_in_catalog("1984", "title")

    # Assert
    assert results == []


def test_search_with_empty_string(monkeypatch):
    """
    Search with empty string should return empty list.
    """
    # Act
    results = search_books_in_catalog("", "title")

    # Assert
    assert results == []


def test_search_with_invalid_type(monkeypatch):
    """
    Search with invalid search type should return empty list.
    """
    # Arrange
    monkeypatch.setattr('services.library_service.get_all_books', lambda: MOCK_CATALOG)

    # Act
    results = search_books_in_catalog("Harry", "invalid_type")

    # Assert
    assert results == []


def test_search_case_insensitive(monkeypatch):
    """
    Search should be case-insensitive.
    """
    # Arrange
    monkeypatch.setattr('services.library_service.get_all_books', lambda: MOCK_CATALOG)

    # Act - Test with different cases
    results_lower = search_books_in_catalog("harry", "title")
    results_upper = search_books_in_catalog("HARRY", "title")
    results_mixed = search_books_in_catalog("HaRrY", "title")

    # Assert - All should return same results
    assert len(results_lower) == 2
    assert len(results_upper) == 2
    assert len(results_mixed) == 2

def test_search_by_isbn_not_found(monkeypatch):
    """Test ISBN search with non-existent book"""
    monkeypatch.setattr('services.library_service.get_book_by_isbn',
                        lambda isbn: None)
    
    results = search_books_in_catalog("9999999999999", "isbn")
    assert results == []


def test_search_by_title_case_variations(monkeypatch):
    """Test case insensitivity with mixed case"""
    monkeypatch.setattr('services.library_service.get_all_books',
                        lambda: [{"id": 1, "title": "HaRrY PoTtEr", "author": "Rowling"}])
    
    results = search_books_in_catalog("HARRY", "title")
    assert len(results) == 1


def test_search_by_author_partial_lowercase(monkeypatch):
    """Test partial author match with lowercase"""
    monkeypatch.setattr('services.library_service.get_all_books',
                        lambda: [{"id": 1, "title": "Book", "author": "J.K. Rowling"}])
    
    results = search_books_in_catalog("rowling", "author")
    assert len(results) == 1
