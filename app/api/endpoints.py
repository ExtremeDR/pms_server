from flask import make_response, request, jsonify
from app.api.query_manager import QueryManager
from app.config import Config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import db,TMP_code,Users_tg,Users,Projects,Sprints, Tasks,Tags, project_user,task_tags
from datetime import datetime, timedelta
from app.api.api_base import APIClient
api = APIClient(db,config)
qm = QueryManager(api)


def _all_projects_by_tg_id_or_user_id():
    params = api.get_params('user_id', 'tg_id', request=request)
    if params.get('tg_id'):
            params['user_id'] = qm.get_user_id(tg_id=params['tg_id'])
    try:
        projects_as_head = api.execute_query(
            select(Projects)
            .where(Projects.head_id == params['user_id'])
        )
        projects_as_member = api.execute_query(
            select(Projects)
            .join(project_user, project_user.c.project_id == Projects.id)
            .where(project_user.c.user_id == params['user_id'])
        )
        projects = []
        projects2 = []
        if projects_as_head or projects_as_member:
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
        return jsonify({'code': 2000,"data": str(e) }), 500

def _tasks():
    params = api.get_params('user_id', 'sprint_id', 'tg_id', request=request)
    # Проверка, чтобы не передавалось несколько параметров одновременно
    if sum(1 for v in params.values() if v is not None) > 1:
        return jsonify({"error": "Please provide only one of 'user_id', 'sprint_id', or 'tg_id'."}), 400
    try:
        TASKS = qm.get_tasks(params)
        return api.to_json(TASKS)
    except Exception as e:
        return jsonify({'code': 2,"data": str(e) }), 500

def _users_in_project():
    param = api.get_params('project_id', request=request)

    try:
        users = api.execute_query(
            select(Users)
            .join(project_user, project_user.c.user_id == Users.id)
            .where(project_user.c.project_id == param['project_id'])
        )

        users_data = []

        if users:
            users_data = [{"id": user.id, "login": user.login, "email": user.email} for user in users]

        return api.to_json(users_data)

    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500

def _sprints_by_project_id():
    param = api.get_params('project_id', request=request)

    try:
        sprints = api.execute_query(
            select(Sprints)
            .where(Sprints.project_id == param['project_id'])
        )

        sprints_data = []

        if sprints:
            sprints_data = [{"id": sprint.id, "start_date": sprint.start_date, "end_date": sprint.end_date} for sprint in sprints]

        return api.to_json(sprints_data)

    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500
