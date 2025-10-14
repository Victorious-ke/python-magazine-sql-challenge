from typing import Optional, List, Any
from .database_utils import get_connection
from .article import Article
from .author import Author

class Magazine:
    def __init__(self, name: str, category: str, id: Optional[int] = None):
        self._validate_name(name)
        self._validate_category(category)
        self._name = name.strip()
        self._category = category.strip()
        self.id = id

    @staticmethod
    def _validate_name(value):
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        if not value.strip():
            raise ValueError("name must be non-empty")

    @staticmethod
    def _validate_category(value):
        if not isinstance(value, str):
            raise TypeError("category must be a string")
        if not value.strip():
            raise ValueError("category must be non-empty")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, v: str) -> None:
        self._validate_name(v)
        self._name = v.strip()

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, v: str) -> None:
        self._validate_category(v)
        self._category = v.strip()

    @classmethod
    def new_from_db(cls, row: Any) -> 'Magazine':
        if row is None:
            return None
        try:
            id_ = row['id']; name = row['name']; category = row['category']
        except Exception:
            id_, name, category = row[0], row[1], row[2]
        return cls(name=name, category=category, id=id_)

    @classmethod
    def find_by_id(cls, id: int) -> Optional['Magazine']:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, category FROM magazines WHERE id = ?;", (id,))
            row = cur.fetchone()
            return cls.new_from_db(row) if row else None
        finally:
            conn.close()

    def save(self) -> None:
        conn = get_connection()
        try:
            cur = conn.cursor()
            if self.id:
                cur.execute("UPDATE magazines SET name = ?, category = ? WHERE id = ?;",
                            (self._name, self._category, self.id))
            else:
                cur.execute("INSERT INTO magazines (name, category) VALUES (?, ?);",
                            (self._name, self._category))
                self.id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()

    # relationships
    def articles(self) -> List[Article]:
        if not self.id:
            return []
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, author_id, magazine_id, title FROM articles WHERE magazine_id = ?;", (self.id,))
            rows = cur.fetchall()
            return [Article.new_from_db(r) for r in rows]
        finally:
            conn.close()

    def contributors(self) -> List[Author]:
        """
        Distinct authors who wrote for this magazine (>=1 article).
        """
        if not self.id:
            return []
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT au.id, au.name
                FROM authors au
                JOIN articles ar ON au.id = ar.author_id
                WHERE ar.magazine_id = ?;
            """, (self.id,))
            rows = cur.fetchall()
            return [Author.new_from_db(r) for r in rows]
        finally:
            conn.close()

    def article_titles(self) -> List[str]:
        if not self.id:
            return []
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT title FROM articles WHERE magazine_id = ?;", (self.id,))
            rows = cur.fetchall()
            return [r['title'] if 'title' in r.keys() else r[0] for r in rows]
        finally:
            conn.close()

    def contributing_authors(self) -> List[Author]:
        """
        Authors who have written more than 2 (i.e., >2) articles in this magazine.
        Uses GROUP BY and HAVING COUNT(id) > 2.
        """
        if not self.id:
            return []
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT au.id, au.name
                FROM authors au
                JOIN articles ar ON au.id = ar.author_id
                WHERE ar.magazine_id = ?
                GROUP BY au.id
                HAVING COUNT(ar.id) > 2;
            """, (self.id,))
            rows = cur.fetchall()
            return [Author.new_from_db(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def top_publisher(cls) -> Optional['Magazine']:
        """
        Bonus: returns the Magazine with the highest number of articles.
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT magazine_id, COUNT(id) as cnt
                FROM articles
                GROUP BY magazine_id
                ORDER BY cnt DESC
                LIMIT 1;
            """)
            row = cur.fetchone()
            if not row:
                return None
            magazine_id = row['magazine_id'] if 'magazine_id' in row.keys() else row[0]
            return cls.find_by_id(magazine_id)
        finally:
            conn.close()

    def __repr__(self):
        return f"<Magazine id={self.id} name={self._name!r} category={self._category!r}>"