from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from back.infrastructure.database.db import db
from back.models.relationships import task_tags


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
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def get_by_head_id(cls, head_id):
        return cls.query.filter_by(head_id=head_id)

class Sprints(db.Model):
    __tablename__ = 'Sprints'
    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('Projects.id', ondelete='CASCADE'), nullable=False)
    status: Mapped[int] = mapped_column(nullable=False)

    tasks = relationship("Tasks", back_populates="sprint_tasks", cascade='all, delete-orphan')
    sprint_projects = relationship("Projects", back_populates="sprints")

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def get_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id)

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

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def get_by_sprint_id(cls, sprint_id):
        return cls.query.filter_by(sprint_id=sprint_id)

class Tags(db.Model):
    __tablename__ = 'Tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    tag_name: Mapped[str] = mapped_column(String(50), unique=True)

    tasks = db.relationship('Tasks', secondary=task_tags, back_populates='tags')
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
