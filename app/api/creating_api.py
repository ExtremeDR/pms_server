from flask import request, jsonify
import app.config as config
from app.config import Config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import *
from datetime import datetime, timedelta

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
        password_hash=generate_password_hash(data.get('password')),
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
        description=project_description,
        start_date= datetime.now,
        status= 1,
        type= 1,
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
        status=1,
        end_date=datetime.now() + timedelta(days=sprint_duration), 
        project_id=project_id
    )
    try:
        db.session.add(new_sprint)
        db.session.commit()
    except Exception as e:
        return jsonify({'success': False, 'code': 2000, 'error' : e}), 400 # Error добавить
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
    if task_duration:
        new_task = Tasks(
            description=task_description,
            task_name=name,
            status = 1,
            set_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=task_duration),
            user_id=user_id,
            sprint_id=sprint_id
        )
    else:
        
        correct_sprint_end_date = db.session.execute(
            select(Sprints.end_date).where(Sprints.id == sprint_id)
            ).scalars().first()  
        
        new_task = Tasks(
            description=task_description,
            task_name=name,
            status = 1,
            set_time=datetime.now(),
            end_time=correct_sprint_end_date,
            user_id=user_id,
            sprint_id=sprint_id
        )
    tags = db.session.execute(
        select(Tags).where(Tags.id.in_(tags))
    ).scalars().all()

    if not tags:
        return jsonify({"error": "No tags found"}), 404
    
    for tag in tags:
        new_task.tags.append(tag)  # Добавляем тег в задачу
    try:
        db.session.add(new_task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'code': 2000, 'error': str(e)}), 500
    return jsonify({'success': True, 'code': 1001})

def _create_tag(secret_code):
    if secret_code != config.code_for_API:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    description = data.get("description") # int
    tag_name = data.get("tag_name")

    new_tag = Tags(
        description=description,
        tag_name=tag_name
    )
    try:
        db.session.add(new_tag)
        db.session.commit()
    except:
        return jsonify({'success': False, 'code': 2000})
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
        sprint_id=existing_task.sprint_id,
        status=1,
    )
    try:
        db.session.add(copied_task)
        db.session.commit()
    except:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    return jsonify({'success': True, 'code': 1001})

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
