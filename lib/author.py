from typing import Optional, List, Any
from .database_utils import get_connection
from .magazine import Magazine

class Author:
    def __init__(self, name: str, id: Optional[int] = None):
        # Validation
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name.strip():
            raise ValueError("name must be non-empty")
        self._name = name.strip()
        self.id = id

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def new_from_db(cls, row: Any) -> Optional["Author"]:
        """
        Create a new Author instance from a database row.
        """
        if row is None:
            return None
        try:
            id_ = row["id"]
            name = row["name"]
        except Exception:
            id_, name = row[0], row[1]
        return cls(name=name, id=id_)

    @classmethod
    def find_by_id(cls, id: int) -> Optional["Author"]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM authors WHERE id = ?;", (id,))
            row = cur.fetchone()
            return cls.new_from_db(row) if row else None
        finally:
            conn.close()

    def save(self) -> None:
        conn = get_connection()
        try:
            cur = conn.cursor()
            if self.id:
                cur.execute("UPDATE authors SET name = ? WHERE id = ?;", (self._name, self.id))
            else:
                cur.execute("INSERT INTO authors (name) VALUES (?);", (self._name,))
                self.id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()

    # Relationships
    def articles(self) -> List["Article"]:
        """
        Return all articles written by this author.
        """
        if not self.id:
            return []
            
        from .article import Article  

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, author_id, magazine_id, title FROM articles WHERE author_id = ?;",
                (self.id,),
            )
            rows = cur.fetchall()
            return [Article.new_from_db(r) for r in rows]
        finally:
            conn.close()

    def magazines(self) -> List[Magazine]:
        """
        Return all distinct magazines this author has written for.
        """
        if not self.id:
            return []
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT DISTINCT m.id, m.name, m.category
                FROM magazines m
                JOIN articles a ON m.id = a.magazine_id
                WHERE a.author_id = ?;
                """,
                (self.id,),
            )
            rows = cur.fetchall()
            return [Magazine.new_from_db(r) for r in rows]
        finally:
            conn.close()

    def add_article(self, magazine: Magazine, title: str) -> "Article":
        """
        Create and save a new article written by this author for a given magazine.
        """
