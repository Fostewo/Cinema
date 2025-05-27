import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Film(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'films'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    release_date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    trailer_url = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    theaters = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'release_date': self.release_date.isoformat(),
            'rating': self.rating,
            'trailer_url': self.trailer_url,
            'theaters': self.theaters
        }
