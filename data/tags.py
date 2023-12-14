import sqlalchemy
from .db_session import SqlAlchemyBase


class Tag(SqlAlchemyBase):
    __tablename__ = 'tag'

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)