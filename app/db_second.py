from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import BigInteger, Column, DateTime, String, ForeignKey, Numeric, Integer, Table, select, MetaData
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
#Base = declarative_base()
# Таблица для связи проектов и участников
project_user = Table(
    'project_user',
    db.metadata,
    Column('project_id', Integer, ForeignKey('Projects.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('Users.id'), primary_key=True)
)

# Таблица для связи задач и тегов
task_tags = Table(
    'task_tags',
    db.metadata,
    Column('task_id', Integer, ForeignKey('Tasks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('Tags.id'), primary_key=True)
)


class Users(db.Model):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)

    telegram_users = relationship("Users_tg", back_populates="user", cascade="all, delete-orphan")
    tmp_codes = relationship("TMP_code", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Projects", back_populates="head", cascade="all, delete-orphan")
    task_user = relationship("Tasks", back_populates="user_task")
    
    project_users = db.relationship('Projects', secondary=project_user, backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Users_tg(db.Model):
    __tablename__ = 'Telegram_Users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'), nullable=False, unique=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    user = relationship("Users", back_populates="telegram_users")


class TMP_code(db.Model):
    __tablename__ = 'TMP_codes'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'), nullable=False, unique=True)
    unic_code: Mapped[str] = mapped_column(nullable=False)

    user = relationship("Users", back_populates="tmp_codes")


class Projects(db.Model):
    __tablename__ = 'Projects'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    head_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    description: Mapped[str] = mapped_column(String(500))
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # Указан Python-тип datetime
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)    # Указан Python-тип datetime
    status: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[int] = mapped_column(nullable=False)

    head = relationship("Users", back_populates="projects")
    sprints = relationship("Sprints", back_populates="sprint_projects")


class Sprints(db.Model):
    __tablename__ = 'Sprints'
    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # Указан Python-тип datetime
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)    # Указан Python-тип datetime
    project_id: Mapped[int] = mapped_column(ForeignKey('Projects.id'))
    status: Mapped[int] = mapped_column(nullable=False)
    
    tasks = relationship("Tasks", back_populates="sprint_tasks")
    sprint_projects = relationship("Projects", back_populates="sprints")


class Tasks(db.Model):
    __tablename__ = 'Tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    #status: Mapped[bool] = mapped_column(db.Boolean(), nullable=False)
    parent_task_id: Mapped[int] = mapped_column(ForeignKey('Tasks.id'), nullable=True)
    status: Mapped[int] = mapped_column(nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    sprint_id: Mapped[int] = mapped_column(ForeignKey('Sprints.id'), nullable=True)
    
    sprint_tasks = relationship("Sprints", back_populates="tasks")
    user_task = relationship("Users", back_populates="task_user")
    connect_tags = db.relationship('Tags', secondary=task_tags, backref='tasks')


class Tags(db.Model):
    __tablename__ = 'Tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    tag_name: Mapped[str] = mapped_column(String(50), unique=True)
    
    #posts = db.relationship('Tasks', secondary=task_tags, backref='tags')



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