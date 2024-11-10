from flask import Flask, request, jsonify, render_template, redirect, url_for
import config
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from db_second import *
from datetime import datetime, timedelta


def _check_telegram_id(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    tID = data.get('telegramID')

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
    
def _add_tg_user(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    code = data.get("uniqueCode")
    tg_id = data.get("tg_id")
    if code is None or tg_id is None:
        return jsonify({'success': False, 'code': 2004}), 400

    tmp_code_entry = db.session.execute(select(TMP_code).where(TMP_code.unic_code == code)).scalars().first()

    if not tmp_code_entry:
        return jsonify({'success': False, 'code': 2005}), 404

    user_id = tmp_code_entry.user_id

    existing_user_tg = db.session.execute(select(Users_tg).where(Users_tg.user_id == user_id)).scalars().first()
    if existing_user_tg:
        return jsonify({'success': False, 'code': 2006}), 400

    new_user_tg = Users_tg(
        user_id=user_id,
        user_tg_id=tg_id
    )

    try:
        tmp_code_entry = db.session.execute(select(TMP_code).where(TMP_code.user_id == user_id)).scalars().first()
        if tmp_code_entry:  
            db.session.delete(tmp_code_entry)  
        db.session.add(new_user_tg) 
        db.session.commit()
        return jsonify({'success': True, 'code': 1001}), 201
    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        return jsonify({'success': False, 'code': 2007, 'message': str(e)}), 500
        
def _gen(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    user_id = data.get('user_id')
    user_code = data.get('uniqueCode')
    new_tmp_code = TMP_code(
        user_id=user_id,
        unic_code=user_code
    )
    try:
        db.session.add(new_tmp_code)  
        db.session.commit() 
        return jsonify({'success': True, 'code': 1001}), 201
    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        return jsonify({'success': False, 'code': 2003,'message': str(e)}), 500
    
def _add_user(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json 

    existing_user_by_login = db.session.execute(
        select(Users).where(Users.login == data.get("login"))
        ).scalars().first()
    existing_user_by_email = db.session.execute(
        select(Users).where(Users.email == data.get("email"))
        ).scalars().first()    
    if existing_user_by_login:
        return jsonify({'success': False, 'code': 2001}), 400
    if existing_user_by_email:
        return jsonify({'success': False, 'code': 2002}), 400

    new_user = Users(
        login=data.get("login"),
        password_hash=generate_password_hash(data.get('pass')),
        email=data.get("email")
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'code': 1001}), 201

def _create_project(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    head_id = data.get("user_id")
    project_title = data.get("project_title")
    project_description = data.get("project_description")

    new_project = Projects(
        title=project_title,
        head_id=head_id,
        description=project_description
    )

    try:
        db.session.add(new_project)
        db.session.commit()
    except:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    return jsonify({'success': True, 'code': 1001})

def _create_sprint(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    project_id = data.get("project_id") # int
    sprint_duration = data.get("sprint_duration") # int

    new_sprint = Sprints(
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=sprint_duration), 
        project_id=project_id
    )
    try:
        db.session.add(new_sprint)
        db.session.commit()
    except:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    return jsonify({'success': True, 'code': 1001})

def _create_task(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    sprint_id = data.get("sprint_id") # int
    user_id = data.get("user_id") # int
    task_description = data.get("task_description")
    task_duration = data.get("task_duration") # int
    tags = data.get('tags_ids') # list with tags_id = [1,2,3]
    name = data.get('name') # list with tags_id = [1,2,3]

    # Создаем задание
    new_task = Tasks(
        description=task_description,
        task_name=name,
        status = 1,
        set_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=task_duration),
        user_id=user_id,
        sprint_id=sprint_id
    )
    tags = db.session.execute(
        select(Tags).where(Tags.id.in_(tags))
    ).scalars().all()

    if not tags:
        return jsonify({"error": "No tags found"}), 404
    # Добавляем теги в задачу
    for tag in tags:
        new_task.tags.append(tag)  # Добавляем тег в задачу
    try:
        db.session.add(new_task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'code': 2000, 'error': str(e)}), 500
    return jsonify({'success': True, 'code': 1001})

def _change_task_status(secret_code):
    data = request.json
    new_status = data.get('status')
    task_id = data.get('task_id')

    # Проверяем, что status передан и является булевым значением
    if new_status is None or not isinstance(new_status, bool):
        return jsonify({'success': False, 'code': 2000}) # Error добавить

    # Находим задачу по task_id
    task = db.session.query(Tasks).get(task_id)

    if not task:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    try:
        task.status = new_status
        db.session.commit()  # Сохраняем изменения в базе данных
    except:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    return jsonify({"success": True, "code": 1001}), 200

def _create_tag(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    description = data.get("description") # int
    tag_name = data.get("tag_name")

    # Создаем тег
    new_tag = Tags(
        description=description,
        tag_name=tag_name
    )
    try:
        db.session.add(new_tag)
        db.session.commit()
    except:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    return jsonify({'success': True, 'code': 1001})

def _create_task_from_other_task(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    task_id = data.get("task_id") # int

    existing_task = db.session.get(Tasks, task_id)

    copied_task = Tasks(
        description=existing_task.description,  
        set_time=datetime.now(),
        end_time=existing_task.end_time,
        user_id=existing_task.user_id,
        sprint_id=existing_task.sprint_id
    )
    try:
        db.session.add(copied_task)
        db.session.commit()
    except:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    return jsonify({'success': True, 'code': 1001})

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
    
def _add_user_to_project(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    user_id = data.get('user_id')  # ID пользователя, которого нужно добавить
    project_id = data.get('project_id')  # ID проекта, в который нужно добавить пользователя

    if not user_id or not project_id:
        return jsonify({'success': False, 'code': 2008}), 400 # Error добавить
    user = db.session.execute(
        select(Users).where(Users.id == user_id)
    ).scalars().first()
    if not user:
        return jsonify({'success': False, 'code': 2009}), 400 # Error добавить

    project = db.session.execute(
        select(Projects).where(Projects.id == project_id)
    ).scalars().first()
    if not project:
        return jsonify({'success': False, 'code': 2010}), 400 # Error добавить

   # Проверка, существует ли уже связь между проектом и пользователем
    existing_member = db.session.execute(
        select(project_user).where(
            project_user.c.project_id == project_id,
            project_user.c.user_id == user_id
        )
    ).scalars().first()

    if existing_member:
        return jsonify({'success': False, 'code': 2011}), 400  # User already in project

    # Добавляем пользователя в проект
    try:
        new_member = project_user.insert().values(project_id=project_id, user_id=user_id)
        db.session.execute(new_member)
        db.session.commit()
        return jsonify({"success": True, 'code': 1001}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'code': 2012, 'message': str(e)}), 500  # Error добавления
    
def _delete_user_from_project(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    user_id = data.get("user_id")
    user_to_delete_id = data.get("user_to_delete_id")
    project_id = data.get("project_id")
    if user_id != db.session.execute(select(Projects.head_id).where(Projects.id == project_id)).scalars().first():
        return jsonify({'success': True,'code' : 2012}), 400
    pr_user = db.session.execute(
        select(project_user).where(
            project_user.c.user_id == user_to_delete_id,
            project_user.c.project_id == project_id
        )
    ).scalars().first()

    if not pr_user:
        return jsonify({'success': False,'code': 2013}), 404
    
    try:
        delete_query = delete(project_user).where(
            project_user.c.user_id == user_to_delete_id,
            project_user.c.project_id == project_id
        )
        db.session.execute(delete_query)
        db.session.commit()
        return jsonify({'success': True, 'code': 1001}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'code': 2000, 'message': str(e)}), 500