from library_service import search_books_in_catalog
import pytest

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
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)

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
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)

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
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
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
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)

    # Act
    results = search_books_in_catalog("1984", "title")

    # Assert
    assert results == []
