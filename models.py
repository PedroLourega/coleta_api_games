from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    cover_image = db.Column(db.String)
    metacritic = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class NewsItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    title = db.Column(db.String, nullable=False)
    summary = db.Column(db.Text)
    source_url = db.Column(db.String, unique=True, nullable=False)
    published_at = db.Column(db.DateTime)
    tag = db.Column(db.String)


class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    store = db.Column(db.String)
    price_old = db.Column(db.Numeric(10, 2))
    price_new = db.Column(db.Numeric(10, 2))
    discount_percent = db.Column(db.Integer)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)


class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
