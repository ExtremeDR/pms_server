from flask import request, jsonify
from app.api.query_manager import QueryManager
from app.api.requesting.RequestManager import Request
from app.config import Config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, or_, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import db,TMP_code,Users_tg,Users,Projects,Sprints, Tasks,Tags, project_user,task_tags
from datetime import datetime, timedelta
from app.api.api_base import APIClient
import traceback
from collections import defaultdict
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
handler = Request(db)
# get_hdl = GetRequest(db)
# get_hdl = GetRequest(db)

def get_user_tasks():
    params = handler.get_params('user_id', 'sprint_id', 'tg_id', request=request)
    tg_id = params.get('tg_id')
    if tg_id:
        fields = [Users_tg.c.user_id]
        filters = [Users_tg.c.tg_id == tg_id]
        user_query = handler.execute_dynamic_query(fields=fields, filters=filters)
        user_id = user_query.scalar()
        if user_id:
            params['user_id'] = user_id
        else:
            return jsonify({'code':2000, 'data':"Hasn`t this tg"}), 404

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
    if params.get("user_id"):
        filters.append(table.user_id == params["user_id"])
    if params.get("sprint_id"):
        filters.append(table.sprint_id == params["sprint_id"])

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
    res = handler.execute_dynamic_query(table, fields, filters, joins, map_results)
    return jsonify(handler.answer(True,res, 1001)),200

def get_sprints():
    params = handler.get_params('project_id', request=request)
    project_id = params.get('project_id')

    if not project_id:
        return jsonify({"error": "Project ID is required", "code": 400}), 400

    try:
        table = Sprints
        fields = [
            table.id, table.start_date, table.end_date, table.status,
            table.project_id
        ]

        filters = [table.project_id == params["project_id"]]

        def map_results(results):
            sprints = []
            for row in results:
                sprints.append({
                    "id": row.id,
                    "start_date": row.start_date,
                    "end_date": row.end_date,
                    "status": row.status
                })
            return sprints

        res = handler.execute_dynamic_query(table, fields, filters, [], map_results)
        return jsonify(handler.answer(True, res, 1001)), 200
    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500

def check_user_exists(data):
    filters = [
        or_(
            Users.login == data.get("login"),
            Users.email == data.get("email")
        )
    ]
    result = handler.execute_dynamic_query(
        table=Users,
        fields=[Users],
        filters=filters
    )
    return result.first() is not None

def _add_user():
    data = request.json
    if handler.check_data("login","password","email",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)", 'youre data':data}, 2000)),400
    if check_user_exists(data):
        return jsonify(handler.answer(False,"User already exists", 2000)),400

    new_user = Users(
        login=data.get("login"),
        password_hash=generate_password_hash(data.get('password')),
        email=data.get("email")
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'code': 1001}), 201