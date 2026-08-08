from datetime import datetime
from models import db

class FavoriteCity(db.Model):
    __tablename__ = 'favorite_cities'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False, unique=True)
    country = db.Column(db.String(10), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'country': self.country or '',
            'added_at': self.added_at.strftime('%Y-%m-%d %H:%M')
        }
