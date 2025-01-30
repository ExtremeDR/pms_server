from collections import defaultdict
import logging

from back.infrastructure.repositories.sqlalchemy_repo import SQLrepository
from back.models.relationships import task_tags
from back.models.structures import Tags, Tasks
from back.models.user import Users_tg


logger = logging.getLogger(__name__)

class TaskController:
    def __init__(self, repository: SQLrepository):
        self.repository = repository


    def get_user_id_from_tg_id(self,tg_id) -> int:
        fields = [Users_tg.user_id]
        filters = [Users_tg.user_tg_id == tg_id]
        user_query = self.repository.execute_dynamic_query(fields=fields, filters=filters)
        user_id = user_query.scalar()
        return user_id
    
    def get_user_tasks(self, user_id=None, sprint_id=None, tg_id=None):
        """
        Получение задач пользователя для указанного спринта и tg_id.
        """
        if not user_id and tg_id:
            user_id = self.get_user_id_from_tg_id(tg_id)
            if not user_id:
                return {'success': False, 'message': "hasnt this tg", 'code': 2000}, 404

        # Формируем запрос для получения задач пользователя
        table = Tasks

        fields = [
            table.id, table.task_name, table.description,
            table.set_time, table.end_time, table.status,
            table.user_id, table.sprint_id,
            Tags.id.label("tag_id"), Tags.tag_name.label("tag_name"),
        ]

        joins = [
            (task_tags, task_tags.c.task_id == table.id, True),
            (Tags, Tags.id == task_tags.c.tag_id, True)
        ]

        filters = []
        if user_id:
            filters.append(table.user_id == user_id)
        if sprint_id:
            filters.append(table.sprint_id == sprint_id)

        def map_results(results):
            tasks = defaultdict(lambda: {"tags": []})
            for row in results:
                task = tasks[row.id]
                task.update({
                    "id": row.id,
                    "task_name": row.task_name,
                    "description": row.description
                })
                if row.tag_id:
                    task["tags"].append({"id": row.tag_id, "name": row.tag_name})
            return list(tasks.values())

        try:
            # Выполняем запрос
            res = self.repository.execute_dynamic_query(fields=fields, filters=filters, joins=joins, result_mapper=map_results)
            return {'success': True, 'data': res, 'code': 1001}, 200
        except Exception as e:
            logger.error(f"Error fetching tasks: {str(e)}")
            return {'success': False, 'message': "Error: " + str(e), 'code': 2000}, 500
