from sqlalchemy import BigInteger, ForeignKey, String, select
from sqlalchemy.orm import relationship, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from back.infrastructure.database.db import db
from back.models.relationships import project_user

class Users(db.Model):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    aboute: Mapped[str] = mapped_column(String(255), nullable=False)

    telegram_users = relationship("Users_tg", back_populates="user", cascade="all, delete-orphan")
    tmp_codes = relationship("TMP_code", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Projects", back_populates="head", cascade="all, delete-orphan")
    task_user = relationship("Tasks", back_populates="user_task", cascade="all, delete-orphan")
    
    project_users = db.relationship('Projects', secondary=project_user, backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def check(self, login, password):
        return check_password_hash(self.password_hash, password) and self.password_hash==login
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    @classmethod
    def get_by_login(cls, login):
        return cls.query.filter_by(login=login).first()

class Users_tg(db.Model):
    __tablename__ = 'Telegram_Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'), nullable=False, unique=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    user = relationship("Users", back_populates="telegram_users")
    
    @classmethod
    def get_by_user_tg_id(cls, user_tg_id):
        return cls.query.filter_by(user_tg_id=user_tg_id).first()
    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

class TMP_code(db.Model):
    __tablename__ = 'TMP_codes'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'), nullable=False, unique=True)
    unic_code: Mapped[str] = mapped_column(String(255), nullable=False)

    user = relationship("Users", back_populates="tmp_codes")