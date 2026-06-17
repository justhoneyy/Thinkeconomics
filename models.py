import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import pytz

db = SQLAlchemy()

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False, default='Macroeconomics')
    description = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(300), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    file_url = db.Column(db.String(300), nullable=True)
    lead_author = db.Column(db.String(100), default='Research Team')
    page_count = db.Column(db.String(20), default='N/A')
    date = db.Column(db.String(50), default=lambda: datetime.now(pytz.timezone('UTC')).strftime('%b %Y'))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('UTC')))

class Podcast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    episode_number = db.Column(db.Integer, nullable=False)
    audio_url = db.Column(db.String(500), nullable=True)
    cover_image = db.Column(db.String(300), nullable=True)
    duration = db.Column(db.String(20), default='30 min')
    date = db.Column(db.String(50), default=lambda: datetime.now(pytz.timezone('UTC')).strftime('%b %d, %Y'))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('UTC')))

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False, default='Economics')
    description = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), default='Staff Writer')
    author_initials = db.Column(db.String(4), default='SW')
    read_time = db.Column(db.String(20), default='5 min read')
    image_url = db.Column(db.String(300), nullable=True)
    featured = db.Column(db.Boolean, default=False)
    date = db.Column(db.String(50), default=lambda: datetime.now(pytz.timezone('UTC')).strftime('%b %Y'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('UTC')))

class Initiative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='fa-chart-bar')
    featured = db.Column(db.Boolean, default=False)
