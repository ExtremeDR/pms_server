from flask import jsonify
from sqlalchemy import select
from app.api.api_base import APIClient
import traceback

class QueryManager:
    def __init__(self, api:APIClient) -> None:
        self.api = api
        pass

    def get_tasks(self,params:dict):
        """
        Получение задач с учетом фильтров и связанных тегов в одном запросе.

        :param params: Словарь с фильтрами 'user_id', 'sprint_id'.
        :return: Список задач в формате JSON.
        """
        try:

            table = self.api.db.metadata.tables["Tasks"]
            tags = self.api.db.metadata.tables.get("Tags")
            tasks_tags = self.api.db.metadata.tables.get("task_tags")

            query = (
                select(
                    table.c.id,
                    table.c.task_name,
                    table.c.description,
                    table.c.set_time,
                    table.c.end_time,
                    table.c.status,
                    table.c.user_id,
                    table.c.sprint_id,
                    tags.c.id.label("tag_id"),
                    tags.c.tag_name.label("tag_name"),
                )
                .join(tasks_tags, tasks_tags.c.task_id == table.c.id, isouter=True)
                .join(tags, tags.c.id == tasks_tags.c.tag_id, isouter=True)
            )

            if params.get("user_id"):
                query = query.where(table.c.user_id == params["user_id"])
            if params.get("sprint_id"):
                query = query.where(table.c.sprint_id == params["sprint_id"])

            res = self.api.execute_query(query)

            from collections import defaultdict

            tasks = defaultdict(lambda: {
                "id": None,
                "title": None,
                "description": None,
                "set_time": None,
                "end_time": None,
                "status": None,
                "user_id": None,
                "sprint_id": None,
                "tags": [],
            })

            for row in res:
                task_id = row.id
                task = tasks[task_id]
                if task["id"] is None:  # Заполняем данные задачи только один раз
                    task.update({
                        "id": row.id,
                        "title": row.task_name,
                        "description": row.description,
                        "set_time": row.set_time,
                        "end_time": row.end_time,
                        "status": row.status,
                        "user_id": row.user_id,
                        "sprint_id": row.sprint_id,
                    })
                if row.tag_id:  # Добавляем теги
                    task["tags"].append({"id": row.tag_id, "tag_name": row.tag_name})

            TASKS = list(tasks.values())

            return TASKS
        except Exception as e:
            return [str(e)]

    def get_user_id(self,*params,request) -> int:
        param = self.api.get_params(params, request=request)

        Users = self.api.db.metadata.tables["Users"]
        Users_tg = self.api.db.metadata.tables.get("Users_tg")

        if not param['user_id'] and param['tg_id']:
            param['user_id'] = self.api.execute_query(
                    select(Users.id)
                    .join(Users_tg, Users_tg.user_id ==Users.id)
                    .where(Users_tg.user_tg_id == param['tg_id'])
                )
        return param['user_id']