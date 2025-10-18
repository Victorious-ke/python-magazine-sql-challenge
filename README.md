#  Python Magazine SQL Challenge

A Python-based object-relational mapping (ORM-lite) project using **SQLite3**.
This project models a publishing system with **Authors**, **Magazines**, and **Articles** — handling persistence, relationships, and business logic using **raw SQL queries**.



##  Features

### Database

* SQLite database: `magazine.db`
* Managed using `lib/database_utils.py`
* Automatically creates and connects to tables with proper **foreign key constraints**:

  * `authors`
  * `magazines`
  * `articles`


####  Author

* Properties:

  * `name` (read-only, validated)
* Methods:

  * `save()` — inserts or updates author in database
  * `articles()` — returns all articles written by the author
  * `magazines()` — returns all magazines this author has contributed to
  * `add_article(magazine, title)` — creates a new article by this author
  * `topic_areas()` — returns unique magazine categories for this author



##  Project Structure

python-magazine-sql-challenge/
│
├── lib/
│   ├── __init__.py
│   ├── database_utils.py
│   ├── author.py
│   ├── magazine.py
│   └── article.py
│
├── tests/
│   ├── test_author.py
│   ├── test_magazine.py
│   └── test_article.py
│
├── debug.py
├── requirements.txt
└── README.md



##  How It Works

1. `create_tables()` in `database_utils.py` builds all tables if they don’t exist.
2. Each class handles its own **CRUD** operations using **raw SQL**.
3. Relationships (like `Author.articles()` or `Magazine.contributors()`) are queried via SQL joins.
4. Data validation ensures:

   * Names and categories are non-empty strings.
   * Articles have valid title, author, and magazine references.



##  Testing

Run all tests:

```bash
pytest -v
```

If you’re running manually:

```bash
python debug.py
```


##  Requirements

* Python 3.8+
* SQLite3
* pytest (for testing)

Install dependencies:

```bash
pip install -r requirements.txt
```



##  Development Commands

Initialize database tables:

```bash
python -m lib.database_utils
```

Run manual tests:

```bash
python debug.py
```

Run automated tests:

```bash
pytest -v
```



##  Git Workflow

```bash
git add -A
git commit -m "Implemented database schema and model logic"
git push origin main
```



##  Author

Developed by **Victorious Ngaruiya**
Phase 3: *Python Magazine SQL Challenge*
A project demonstrating database persistence and OOP integration using SQLite and Python.


