from flask import request, jsonify
from app.config import Config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import *
from datetime import datetime, timedelta

def _change_task_status(secret_code):
    data = request.json
    new_status = data.get('status')
    task_id = data.get('task_id')

    if new_status is None or not isinstance(new_status, int):
        return jsonify({'success': False, 'code': 2000}) # Error добавить

    task = db.session.query(Tasks).get(task_id)

    if not task:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    try:
        task.status = new_status
        db.session.commit()  # Сохраняем изменения в базе данных
    except:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    return jsonify({"success": True, "code": 1001}), 200

def _change_project_status_and_sprints(secret_code):
    data = request.json
    new_status = data.get('status')
    project_id = data.get('project_id')

    if new_status is None or not isinstance(new_status, int):
        return jsonify({'success': False, 'code': 2000})  # Ошибка, статус не передан или неверный формат

    project = db.session.execute(select(Projects).filter(Projects.id == project_id)).scalar_one_or_none()

    if not project:
        return jsonify({'success': False, 'code': 2000})  # Ошибка, проект не найден

    try:
        project.status = new_status
        sprints = db.session.execute(select(Sprints).filter(Sprints.project_id == project_id, Sprints.status == 1)).scalars().all()
        
        for sprint in sprints:
            sprint.status = 3  # Изменяем статус спринта на 3
            tasks = db.session.execute(select(Tasks).filter(Tasks.sprint_id == sprint.id)).scalars().all()
            
            for task in tasks:
                
                if task.status != 2:  # Если статус задачи не равен 2
                    
                    task.status = 3  # Обновляем статус задачи на 3
        db.session.commit()  # Сохраняем изменения в базе данных
    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        return jsonify({'success': False, 'code': 2000, 'message': str(e)})  # Ошибка при сохранении

    return jsonify({"success": True, "code": 1001}), 200  # Успех

def _change_sprint_status(secret_code):
    data = request.json
    new_status = data.get('status')
    sprint_id = data.get('sprint_id')

    if new_status is None or not isinstance(new_status, int):
        return jsonify({'success': False, 'code': 2000}) # Error добавить

    sprint = db.session.execute(select(Sprints).filter(Sprints.id == sprint_id)).scalar_one_or_none()
    if not sprint:
        return jsonify({'success': False, 'code': 2000}) # Error добавить
    try:
        sprint.status = new_status

        tasks = db.session.execute(select(Tasks).filter(Tasks.sprint_id == sprint_id)).scalars().all()
        for task in tasks:
            if task.status != 2:  # Если статус задачи не равен 2
                task.status = 3  # Обновляем статус задачи на 3

        db.session.commit()  # Сохраняем изменения в базе данных
    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        return jsonify({'success': False, 'code': 2000, 'message': str(e)})  # Ошибка при сохранении

    return jsonify({"success": True, "code": 1001}), 200  # Успех
