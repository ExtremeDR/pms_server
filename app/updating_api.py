from flask import request, jsonify
import app.config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import *
from datetime import datetime, timedelta

def _change_task_status(secret_code):
    data = request.json
    new_status = data.get('status')
    task_id = data.get('task_id')

    # Проверяем, что status передан и является булевым значением
    if new_status is None or not isinstance(new_status, int):
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