from flask import request, jsonify
from app.config import Config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, select,delete
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import *
from datetime import datetime, timedelta

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