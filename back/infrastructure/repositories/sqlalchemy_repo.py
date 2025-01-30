import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class SQLrepository:
    model = None

    def __init__(self, db: SQLAlchemy):
        self.db = db
    def execute_dynamic_query(self, fields, filters=None, joins=None, result_mapper=None):
        """
        Выполняет запрос к базе данных с параметрами:
        - fields: список полей для выборки.
        - filters: список фильтров (опционально).
        - joins: список джойнов (опционально).
        - result_mapper: функция для обработки результата (опционально).
        """
        query = select(*fields)

        if joins:
            for join_table, condition, is_outer in joins:
                query = query.join(join_table, condition, isouter=is_outer)

        if filters:
            for condition in filters:
                query = query.where(condition)

        results = self.db.session.execute(query)

        if result_mapper:
            return result_mapper(results)

        return results
    
    def add(self, item):
        try:
            self.db.session.add(item)
            self.db.session.commit()
        except Exception as e:
            logger.error(f"Unexpected exception: {e}")
            raise e
        
    def insert(self, item1, item2):
        """
        Добавляет объект в базу данных и сохраняет изменения.
        """
        try:
            self.db.session
        except Exception as e:
            logger.error(f"Unexpected exception: {e}")
            raise e
        
    def insert_dynamic(self, table, values: dict):
        """
        Выполняет вставку динамических данных в указанную таблицу.
        :param table: объект таблицы.
        :param values: словарь значений для вставки.
        """
        try:
            insert_stmt = table.insert().values(**values)
            self.db.session.execute(insert_stmt)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Unexpected exception: {e}")
            raise e
        
    def delete(self, model, filters):
        try:
            self.db.session.query(model).filter(*filters).delete()
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting item: {e}")
            raise e

    def update(self, model, filters, updates):
        try:
            self.db.session.query(model).filter(*filters).update(updates)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating item: {e}")
            raise e

    def exists(self, model, filters):
        return self.db.session.query(model).filter(*filters).first() is not None
    
    def get_one(self, model, filters):
        """
        Получает одну запись из таблицы, соответствующую фильтрам.
        """
        try:
            return self.db.session.query(model).filter(*filters).first()
        except Exception as e:
            logger.error(f"Error fetching item: {e}")
            return None