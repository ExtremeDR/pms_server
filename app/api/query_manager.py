from flask import jsonify
from sqlalchemy import select
from api_base import APIClient

class QueryManager:
    def __init__(self, api:APIClient) -> None:
        self.api = api
        pass
    
    def get_tasks(self,params:dict):
        
        if params.get('tg_id'):
            params['user_id'] = self.get_user_id('user_id', 'tg_id')
        
        query = select(self.api.db.Tasks)
        
        if params.get('user_id'):
            query = query.where(self.api.db.Tasks.user_id == params['user_id'])
        
        if params.get('sprint_id'):
            query = query.where(self.api.db.Tasks.sprint_id == params['sprint_id'])
            
        TASKS=[]
        for task in query:
            task_tag = self.api.execute_query(
                select(self.api.db.Tags)
                .join(self.api.db.task_tags, self.api.db.task_tags.c.tag_id == self.api.db.Tags.id)
                .where(self.api.db.task_tags.c.task_id == task.id)
            )
            TASK = {
                "id": task.id,
                "title": task.task_name,
                "description": task.description,
                "set_time": task.set_time,
                "end_time": task.end_time,
                "status": task.status,
                "user_id": task.user_id,
                "sprint_id": task.sprint_id if not None else 0,
                "tags": [{"id": tag.id, "tag_name": tag.tag_name} for tag in task_tag],
            }
            TASKS.append(TASK)
        return TASKS
        
    def get_user_id(self,*params) -> int:
        param = self.api.get_params(params)
        
        if not param['user_id'] and param['tg_id']:
            param['user_id'] = self.api.execute_query(
                    select(self.api.db.Users.id)
                    .join(self.api.db.Users_tg, self.api.db.Users_tg.user_id == self.api.db.Users.id)
                    .where(self.api.db.Users_tg.user_tg_id == param['tg_id'])
                ) 
        return param['user_id']