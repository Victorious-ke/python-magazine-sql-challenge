from lib.database_utils import create_tables
from lib.author import Author
from lib.magazine import Magazine

def setup_module(module):
    create_tables()

def test_author_can_add_article():
    a = Author("Alice")
    a.save()
    m = Magazine("Tech Monthly", "Technology")
    m.save()
    art = a.add_article(m, "AI in 2025")
    assert art.title == "AI in 2025"
    assert art.author.name == "Alice"
