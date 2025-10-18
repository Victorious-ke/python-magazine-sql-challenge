from typing import Optional, Any
from .database_utils import get_connection


class Article:
    def __init__(self, author: "Author", magazine: "Magazine", title: str, id: Optional[int] = None):
        from .author import Author
        from .magazine import Magazine

        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if not title.strip():
            raise ValueError("title must be non-empty")

        if not isinstance(author, Author):
            raise TypeError("author must be an Author instance")
        if not isinstance(magazine, Magazine):
            raise TypeError("magazine must be a Magazine instance")

        self._title = title.strip()
        self._author = author
        self._magazine = magazine
        self.id = id

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> "Author":
        return self._author

    @author.setter
    def author(self, val: "Author"):
        from .author import Author
        if not isinstance(val, Author):
            raise TypeError("author must be an Author instance")
        self._author = val

    @property
    def magazine(self) -> "Magazine":
        return self._magazine

    @magazine.setter
    def magazine(self, val: "Magazine"):
        from .magazine import Magazine
        if not isinstance(val, Magazine):
            raise TypeError("magazine must be a Magazine instance")
        self._magazine = val

    @classmethod
    def new_from_db(cls, row: Any) -> Optional["Article"]:
        """
        row expected columns: id, author_id, magazine_id, title
        Uses Author.find_by_id() and Magazine.find_by_id() to attach full objects.
        """
        if row is None:
            return None

        try:
            id_ = row["id"]
            author_id = row["author_id"]
            magazine_id = row["magazine_id"]
            title = row["title"]
        except Exception:
            id_, author_id, magazine_id, title = row[0], row[1], row[2], row[3]

        from .author import Author
        from .magazine import Magazine

        author_obj = Author.find_by_id(author_id)
        magazine_obj = Magazine.find_by_id(magazine_id)

        return cls(author=author_obj, magazine=magazine_obj, title=title, id=id_)

    @classmethod
    def find_by_id(cls, id: int) -> Optional["Article"]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, author_id, magazine_id, title FROM articles WHERE id = ?;", (id,))
            row = cur.fetchone()
            return cls.new_from_db(row) if row else None
        finally:
            conn.close()

    def save(self) -> None:
        """
        Insert or update. Use author.id and magazine.id as foreign keys.
        """
        from .author import Author
        from .magazine import Magazine

        if not self._author or not isinstance(self._author, Author):
            raise TypeError("author must be an Author instance before saving")
        if not self._magazine or not isinstance(self._magazine, Magazine):
            raise TypeError("magazine must be a Magazine instance before saving")

        if not self._author.id:
            self._author.save()
        if not self._magazine.id:
            self._magazine.save()

        conn = get_connection()
        try:
            cur = conn.cursor()
            if self.id:
                cur.execute(
                    """
                    UPDATE articles
                    SET author_id = ?, magazine_id = ?, title = ?
                    WHERE id = ?;
                    """,
                    (self._author.id, self._magazine.id, self._title, self.id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO articles (author_id, magazine_id, title)
                    VALUES (?, ?, ?);
                    """,
                    (self._author.id, self._magazine.id, self._title),
                )
                self.id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()

    def __repr__(self):
        return (
            f"<Article id={self.id} title={self._title!r} "
            f"author_id={getattr(self._author, 'id', None)} "
            f"magazine_id={getattr(self._magazine, 'id', None)}>"
        )
