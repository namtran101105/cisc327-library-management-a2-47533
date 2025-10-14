import pytest
from library_service import search_books_in_catalog

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

def test_search_by_title_partial_match(monkeypatch):
    """
    Happy path: Partial title search (case-insensitive).
    Query "harry" should match 2 books with "Harry" in title.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("harry", "title")
    
    assert len(results) == 2
    assert results[0]["title"] == "Harry Potter and the Sorcerer's Stone"
    assert results[1]["title"] == "Harry Potter and the Chamber of Secrets"


def test_search_by_author_partial_match(monkeypatch):
    """
    Happy path: Partial author search (case-insensitive).
    Query "rowling" should match 2 books by J.K. Rowling.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("rowling", "author")
    
    assert len(results) == 2
    assert all("Rowling" in r["author"] for r in results)


def test_search_by_isbn_exact_match(monkeypatch):
    """
    Happy path: ISBN search requires exact match.
    Should return exactly 1 book with matching ISBN.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("9780618260300", "isbn")
    
    assert len(results) == 1
    assert results[0]["title"] == "The Hobbit"


def test_search_title_all_uppercase(monkeypatch):
    """
    Case-insensitivity test: All uppercase query.
    "HARRY" should match books with "Harry" (case-insensitive).
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("HARRY", "title")
    
    assert len(results) == 2
    assert results[0]["title"] == "Harry Potter and the Sorcerer's Stone"


def test_search_title_mixed_case(monkeypatch):
    """
    Case-insensitivity test: Mixed case query.
    "HaRrY pOtTeR" should match Harry Potter books.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("HaRrY pOtTeR", "title")
    
    assert len(results) == 2


def test_search_no_matches(monkeypatch):
    """
    Edge case: Search term with no matches.
    Should return empty list.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("Nonexistent Book", "title")
    
    assert results == []


def test_search_empty_search_term(monkeypatch):
    """
    Edge case: Empty search term.
    Should return empty list without querying database.
    """
    results = search_books_in_catalog("", "title")
    
    assert results == []


def test_search_whitespace_only_term(monkeypatch):
    """
    Edge case: Whitespace-only search term.
    Should be treated as empty and return empty list.
    """
    results = search_books_in_catalog("   ", "title")
    
    assert results == []


def test_search_invalid_search_type(monkeypatch):
    """
    Input validation: Invalid search type.
    Only "title", "author", "isbn" are valid.
    Should return empty list for invalid types.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("Harry", "invalid_type")
    
    assert results == []


def test_search_empty_search_type(monkeypatch):
    """
    Edge case: Empty search type string.
    Should return empty list.
    """
    results = search_books_in_catalog("Harry", "")
    
    assert results == []


def test_search_isbn_partial_no_match(monkeypatch):
    """
    Business rule: ISBN search is exact-only (no partial match).
    Partial ISBN should return empty list.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("97806182", "isbn")
    
    assert results == []


def test_search_author_with_special_chars(monkeypatch):
    """
    Edge case: Author name with periods (J.K., J.R.R.).
    Should match correctly including special characters.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("J.K.", "author")
    
    assert len(results) == 2


def test_search_single_character(monkeypatch):
    """
    Boundary test: Single character search.
    Should return all books with that letter in the field.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: MOCK_CATALOG)
    
    results = search_books_in_catalog("H", "title")
    
    assert len(results) >= 2  # Harry and Hobbit


def test_search_empty_catalog(monkeypatch):
    """
    Edge case: Search in empty catalog.
    Should return empty list gracefully.
    """
    monkeypatch.setattr('database.get_all_books_for_search', lambda: [])
    
    results = search_books_in_catalog("Harry", "title")
    
    assert results == []
