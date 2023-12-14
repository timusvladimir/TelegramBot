from datetime import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = "news"

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # json
    date_of_creation = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    weight = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    news_markup = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return f'<News> {self.id} {self.title} {self.weight}'