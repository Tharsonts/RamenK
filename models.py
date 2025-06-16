from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Importação circular resolvida
db = None

def init_db(database):
    global db
    db = database

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MenuSection(db.Model):
    __tablename__ = 'menu_sections'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    subtitle = db.Column(db.String(200))
    position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com itens
    items = db.relationship('MenuItem', backref='section', lazy=True, cascade='all, delete-orphan')
    subsections = db.relationship('MenuSubsection', backref='section', lazy=True, cascade='all, delete-orphan')


class MenuSubsection(db.Model):
    __tablename__ = 'menu_subsections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)
    section_id = db.Column(db.Integer, db.ForeignKey('menu_sections.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com itens
    items = db.relationship('MenuItem', backref='subsection', lazy=True, cascade='all, delete-orphan')


class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.String(20), nullable=False)
    image_path = db.Column(db.String(200))
    position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    section_id = db.Column(db.Integer, db.ForeignKey('menu_sections.id'), nullable=False)
    subsection_id = db.Column(db.Integer, db.ForeignKey('menu_subsections.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)