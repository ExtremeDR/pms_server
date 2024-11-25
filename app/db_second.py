from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import BigInteger, Column, DateTime, String, ForeignKey, Numeric, Integer, Table, select, MetaData
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from flask_migrate import Migrate # type: ignore

db = SQLAlchemy()
migrate = Migrate()
#Base = declarative_base()
# Таблица для связи проектов и участников
project_user = Table(
    'project_user',
    db.metadata,
    Column('project_id', Integer, ForeignKey('Projects.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('Users.id', ondelete='CASCADE'), primary_key=True)
)

# Таблица для связи задач и тегов
task_tags = Table(
    'task_tags',
    db.metadata,
    Column('task_id', Integer, ForeignKey('Tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('Tags.id', ondelete='CASCADE'), primary_key=True)
)


class Users(db.Model):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    telegram_users = relationship("Users_tg", back_populates="user", cascade="all, delete-orphan")
    tmp_codes = relationship("TMP_code", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Projects", back_populates="head", cascade="all, delete-orphan")
    task_user = relationship("Tasks", back_populates="user_task", cascade="all, delete-orphan")
    
    project_users = db.relationship('Projects', secondary=project_user, backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Users_tg(db.Model):
    __tablename__ = 'Telegram_Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'), nullable=False, unique=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    user = relationship("Users", back_populates="telegram_users")


class TMP_code(db.Model):
    __tablename__ = 'TMP_codes'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'), nullable=False, unique=True)
    unic_code: Mapped[str] = mapped_column(String(255), nullable=False)

    user = relationship("Users", back_populates="tmp_codes")


class Projects(db.Model):
    __tablename__ = 'Projects'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    head_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(String(500))
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[int] = mapped_column(nullable=False)

    head = relationship("Users", back_populates="projects")
    sprints = relationship("Sprints", back_populates="sprint_projects", cascade='all, delete-orphan')


class Sprints(db.Model):
    __tablename__ = 'Sprints'
    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('Projects.id', ondelete='CASCADE'), nullable=False)
    status: Mapped[int] = mapped_column(nullable=False)

    tasks = relationship("Tasks", back_populates="sprint_tasks", cascade='all, delete-orphan')
    sprint_projects = relationship("Projects", back_populates="sprints")


class Tasks(db.Model):
    __tablename__ = 'Tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[int] = mapped_column(nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id', ondelete='CASCADE'))
    sprint_id: Mapped[int] = mapped_column(ForeignKey('Sprints.id', ondelete='CASCADE'), nullable=True)

    sprint_tasks = relationship("Sprints", back_populates="tasks")
    user_task = relationship("Users", back_populates="task_user")
    tags = db.relationship('Tags', secondary=task_tags, back_populates='tasks')


class Tags(db.Model):
    __tablename__ = 'Tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    tag_name: Mapped[str] = mapped_column(String(50), unique=True)

    tasks = db.relationship('Tasks', secondary=task_tags, back_populates='tags')



'''  
# Таблица для связи спринтов и проектов
project_sprints = Table(
    'project_sprints',
    db.metadata,
    Column('project_id', Integer, ForeignKey('Projects.id'), primary_key=True),
    Column('sprint_id', Integer, ForeignKey('Sprints.id'), primary_key=True)
)

# Таблица для связи спринтов и задач
sprint_tasks = Table(
    'sprint_tasks',
    db.metadata,
    Column('sprint_id', Integer, ForeignKey('Sprints.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('Tasks.id'), primary_key=True)
)
''' 
    
def init_db():
    try:
        db.create_all()  # Создает таблицы, если они еще не существуют
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")