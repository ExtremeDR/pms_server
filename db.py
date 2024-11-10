from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import BigInteger, DateTime, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(BigInteger, nullable=False, unique=True)
    login = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    password_hash = db.Column(String, nullable=False)  # Хранит хеш пароля
    email = db.Column(String, nullable=False)
    def set_password(self, password):
        """Хеширует пароль и сохраняет его в поле password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет пароль, сравнивая его с хешем в базе данных."""
        return check_password_hash(self.password_hash, password)
    
    
    telegram_users = relationship("Users_tg", back_populates="user", cascade="all, delete-orphan")
    tmp_codes = relationship("TMP_code", back_populates="user", cascade="all, delete-orphan")
    
class Users_tg(db.Model):
    __tablename__ = 'Telegram_Users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, ForeignKey('Users.user_id'), nullable=False, unique=True)  # Добавлен ForeignKey
    user_tg_id = db.Column(BigInteger, unique=True)
    # Связь с таблицей Users
    user = relationship("Users", back_populates="telegram_users")

    

class TMP_code(db.Model):
    __tablename__ = 'TMP_codes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, ForeignKey('Users.user_id'), nullable=False, unique=True)  # Добавлен ForeignKey
    unic_code = db.Column(db.String, nullable=False)
    
    # Связь с таблицей Users
    user = relationship("Users", back_populates="tmp_codes")


def init_db():
    try:
        db.create_all()  # Создает таблицы, если они еще не существуют
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")