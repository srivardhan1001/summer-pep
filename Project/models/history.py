from datetime import datetime
from models import db

class SearchHistory(db.Model):
    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(10), nullable=True)
    temperature = db.Column(db.Float, nullable=False)
    weather = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'country': self.country or '',
            'temperature': round(self.temperature, 1),
            'weather': self.weather,
            'icon': self.icon or '01d',
            'date': self.created_at.strftime('%Y-%m-%d'),
            'time': self.created_at.strftime('%H:%M')
        }
