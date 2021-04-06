from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from datetime import datetime

Base = declarative_base()


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


class GbIdMixin:
    id = Column(Integer, primary_key=True, autoincrement=False)


class NameMixin:
    name = Column(String)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Author(Base, IdMixin, NameMixin, UrlMixin):
    __tablename__ = "author"
    posts = relationship("Post")
    comments = relationship("Comment")


class Post(Base, GbIdMixin, UrlMixin):
    __tablename__ = "post"
    title = Column(String, nullable=False)
    img = Column(String)
    date = Column(DateTime)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author")
    comments = relationship("Comment")
    tags = relationship("Tag", secondary=tag_post)


class Tag(Base, IdMixin, NameMixin, UrlMixin):
    __tablename__ = "tag"
    posts = relationship(Post, secondary=tag_post)


class Comment(Base, GbIdMixin):
    __tablename__ = "comment"
    parent_id = Column(Integer)
    root_comment_id = Column(Integer)
    body = Column(String)
    created_at = Column(DateTime)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship(Post)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author")

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.parent_id = kwargs["parent_id"]
        self.root_comment_id = kwargs["root_comment_id"]
        self.body = kwargs["body"]
        self.created_at = datetime.fromisoformat(kwargs["created_at"])
        self.author = kwargs["author"]
