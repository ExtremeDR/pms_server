import os
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

def init_db():
    try:
        db.create_all()  # Создает таблицы, если они еще не существуют
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")