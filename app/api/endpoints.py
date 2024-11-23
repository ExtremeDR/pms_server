from flask import make_response, request, jsonify
from app.api.query_manager import QueryManager
from app.api.requesting.RequestManager import GetRequest
from app.config import Config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import db,TMP_code,Users_tg,Users,Projects,Sprints, Tasks,Tags, project_user,task_tags
from datetime import datetime, timedelta
from app.api.api_base import APIClient
import traceback
api = APIClient(db,config)
qm = QueryManager(api)


def _all_projects_by_tg_id_or_user_id():
    params = api.get_params('user_id', 'tg_id', request=request)
    if params.get('tg_id'):
            params['user_id'] = qm.get_user_id(params.get('tg_id'))
    try:
        projects_as_head = api.execute_query(
            select(Projects.id.label('id'), Projects.title.label('title'), Projects.description.label('description'))
            .where(Projects.head_id == params['user_id'])
        )

        projects_as_member = api.execute_query(
            select(Projects.id.label('id'), Projects.title.label('title'), Projects.description.label('description'))
            .join(project_user, project_user.c.project_id == Projects.id)
            .where(project_user.c.user_id == params['user_id'])
        )
        projects = []
        projects2 = []
        if projects_as_head or projects_as_member:
            if len(projects_as_head) > 0 or len(projects_as_member) > 0:
                projects = [
                    {
                        "id": project.id,
                        "title": project.title,
                        "description": project.description,
                        "role": True
                    }
                    for project in projects_as_head
                ]
                projects2 = [
                    {
                        "id": project.id,
                        "title": project.title,
                        "description": project.description,
                        "role": False
                    }
                    for project in projects_as_member
                ]
        return api.to_json(projects+projects2)
    except Exception as e:
        return jsonify({'code': 2000,"data": str(e)}), 500

def _tasks():
    params = api.get_params('user_id', 'sprint_id', 'tg_id', request=request)
    # Проверка, чтобы не передавалось несколько параметров одновременно
    if sum(1 for v in params.values() if v is not None) > 1:
        return jsonify({"error": "Please provide only one of 'user_id', 'sprint_id', or 'tg_id'."}), 400
    try:
        TASKS = qm.get_tasks(params)
        return api.to_json(TASKS)
    except Exception as e:
        return jsonify({'code': 2000,"data": str(e) }), 500

def _users_in_project():
    param = api.get_params('project_id', request=request)

    try:
        users = api.execute_query(
            select(Users.id.label('id'),Users.email.label('email'),Users.login.label('login'))
            .join(project_user, project_user.c.user_id == Users.id)
            .where(project_user.c.project_id == param['project_id'])
        )

        users_data = []

        if users:
            users_data = [{"id": user.id, "login": user.login, "email": user.email} for user in users]

        return api.to_json(users_data)

    except:
        return jsonify({"data": traceback.format_exc(), 'code': 2000}), 500

def get_sprints_by_project_id(project_id):
    return api.execute_query(
        select(Sprints.id.label('id'),
               Sprints.start_date.label('start_date'),
               Sprints.end_date.label('end_date'),
               Sprints.status.label('status'))
        .where(Sprints.project_id == project_id)
    )
def format_sprints_data(sprints):
    return [{
        "id": sprint.id,
        "start_date": sprint.start_date,
        "end_date": sprint.end_date,
        "status": sprint.status
    } for sprint in sprints]

def _sprints_by_project_id():
    param = api.get_params('project_id', request=request)
    project_id = param.get('project_id')

    if not project_id:
        return jsonify({"error": "Project ID is required", "code": 400}), 400

    try:
        sprints = get_sprints_by_project_id(project_id)
        sprints_data = format_sprints_data(sprints) if sprints else []
        return api.to_json(sprints_data)
    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500

#################################################################
###################       New API          ######################
#################################################################

def get_user_tasks():
    handler = GetRequest()
    params = api.get_params('user_id', 'sprint_id', 'tg_id', request=request)
    tg_id = params.get('tg_id')
    if tg_id:
        fields = [Users_tg.c.user_id]
        filters = [Users_tg.c.tg_id == tg_id]
        user_query = handler.execute_dynamic_query(fields=fields, filters=filters)
        user_id = user_query.scalar()  # Получаем user_id как одиночное значение
        if user_id:
            params['user_id'] = user_id  # Добавляем user_id в результат
        else:
            return jsonify({'code':2000, 'data':"Hasn`t this tg"}), 404
        
    table = Tasks
    
    fields = [
        table.c.id, table.c.task_name, table.c.description,
        table.c.set_time, table.c.end_time, table.c.status,
        table.c.user_id, table.c.sprint_id,
        Tags.c.id.label("tag_id"), Tags.c.tag_name.label("tag_name"),
    ]

    joins = [
        (task_tags, task_tags.c.task_id == table.c.id, True),
        (Tags, Tags.c.id == task_tags.c.tag_id, True)
    ]

    filters = []
    if params.get("user_id"):
        filters.append(table.c.user_id == params["user_id"])
    if params.get("sprint_id"):
        filters.append(table.c.sprint_id == params["sprint_id"])

    def map_results(results):
        return [
            {
                "id": row.id,
                "task_name": row.task_name,
                "description": row.description,
                "tag": {"id": row.tag_id, "name": row.tag_name},
            }
            for row in results
        ]

    return jsonify(handler.answer(True,handler.execute_dynamic_query(table, fields, filters, joins, map_results, 1001))),200
