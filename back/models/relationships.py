
from sqlalchemy import Column, ForeignKey, Integer, Table

from back.infrastructure.database.db import db

class project_user(db.Model):
    __tablename__ = "project_user"
    
    project_id = Column(Integer, ForeignKey('Projects.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id', ondelete='CASCADE'), primary_key=True)

class task_tags(db.Model):
    __tablename__ = "task_tags"
    
    task_id = Column(Integer, ForeignKey('Tasks.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('Tags.id', ondelete='CASCADE'), primary_key=True)
    