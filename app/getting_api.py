from flask import request, jsonify
import app.config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import *
from datetime import datetime, timedelta

def _check_telegram_id(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    tID = data.get('tg_id')

    exists = db.session.execute(
        select(Users_tg).where(Users_tg.user_tg_id == tID)
    ).scalars().first() is not None
    
    if exists:
        exists = "True"
    else:
        exists = "False"
        
    response = {'exists': exists}
    return jsonify(response)


def _is_user_exists(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    login = data.get('login')
    pas = data.get('password')

    user = db.session.execute(
        select(Users).where(Users.login == login)
    ).scalars().first()
    
    if user:
        is_true_pass = Users.check_password(user, pas)
        exists = "True" if is_true_pass else "False"
    else:
        exists = "False"
        
    response = {'exists': exists}
    return jsonify(response)

def _all_projects_by_login(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    date = request.json
    user_login = date.get("login")

    try:
        result = db.session.execute(
            select(Projects)
            .join(project_user, project_user.c.project_id == Projects.id)
            .join(Users, project_user.c.user_id == Users.id)
            .where(Users.login == user_login)
        ).scalars().all()
        if result:
            projects = [{"id": project.id, "title": project.title, "description": project.description} for project in result]
            return jsonify({'data' : projects, 'code' : 1001}), 200
        else:
            return jsonify({"data": "No projects found for this user.", 'code': 2000}), 404

    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500
    
def _projects_by_head_id(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    user_id = data.get("user_id")

    try:
       
        projects = db.session.execute(
            select(Projects)
            .where(Projects.head_id == user_id)
        ).scalars().all()

        if projects:
            projects_data = [{"id": project.id, "title": project.title, "description": project.description} for project in projects]
            return jsonify({'data' : projects_data, 'code' : 1001}), 200
        else:
            return jsonify({"data": "No projects found for this user.", 'code': 2000}), 404

    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500
    
def _sprints_by_project_id(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    project_id = data.get("project_id")

    try:
        sprints = db.session.execute(
            select(Sprints)
            .where(Sprints.project_id == project_id)
        ).scalars().all()

        if sprints:
            sprints_data = [{"id": sprint.id, "start_date": sprint.start_date, "end_date": sprint.end_date} for sprint in sprints]
            return jsonify({'data' : sprints_data, 'code' : 1001}), 200
        else:
            return jsonify({"data": "No projects found for this user.", 'code': 2000}), 404

    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500
    
def _tasks_by_sprint_id(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    sprint_id = data.get("sprint_id")

    try:
        tasks = db.session.execute(
            select(Tasks)
            .where(Tasks.sprint_id == sprint_id)
        ).scalars().all()

        tasks_data = []
        for task in tasks:
            task_tag = db.session.execute(
                select(Tags)
                .join(task_tags, task_tags.c.tag_id == Tags.id)
                .where(task_tags.c.task_id == task.id)
            ).scalars().all()
            
            task_data = {
                "task_id": task.id,
                "task_name": task.task_name,
                "description": task.description,
                "tags": [{"id": tag.id, "tag_name": tag.tag_name} for tag in task_tag]
            }
            tasks_data.append(task_data)

        return jsonify({'data' : tasks_data, 'code' : 1001}), 200
    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500
    
def _users_in_project(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    project_id = data.get("project_id")

    try:
        users = db.session.execute(
            select(Users)
            .join(project_user, project_user.c.user_id == Users.id)
            .where(project_user.c.project_id == project_id)
        ).scalars().all()

        if users:
            users_data = [{"id": user.id, "login": user.login, "email": user.email} for user in users]
            return jsonify({'data' : users_data, 'code' : 1001}), 200
        else:
            return jsonify({"data": "No users found for this project.", 'code':2000}), 404

    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500
    
def _all_projects_by_tg_id(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    tg_id = data.get("tg_id")
    id = data.get("user_id")
    if not id:
        id = db.session.execute(
                select(Users.id)
                .join(Users_tg, Users_tg.user_id == Users.id)
                .where(Users_tg.user_tg_id == tg_id)
            ).scalar()
    try: 
        projects_as_head = db.session.execute(
            select(Projects)
            .where(Projects.head_id == id)  # Проверяем, является ли пользователь главой проекта
        ).scalars().all()
        projects_as_member = db.session.execute(
            select(Projects)
            .join(project_user, project_user.c.project_id == Projects.id)  # Соединяем с таблицей участников проекта
            .where(project_user.c.user_id == id)  # Проверяем, является ли пользователь участником
        ).scalars().all()
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
            return jsonify({'data': projects+projects2, 'code': 1001}), 200
        else:
            return jsonify({"data": "No projects found for this user.", 'code': 2000}), 404
    except Exception as e:
        return jsonify({"data": str(e), 'code': 2000}), 500