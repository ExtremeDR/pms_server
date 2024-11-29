from flask import request, jsonify
from app.api.requesting.RequestManager import Request
from app.config import Config as config
from werkzeug.security import generate_password_hash
from sqlalchemy import case, or_, select,delete
from app.db_second import db,TMP_code,Users_tg,Users,Projects,Sprints, Tasks,Tags, project_user,task_tags
from datetime import datetime, timedelta
import traceback
from collections import defaultdict


handler = Request(db)
#################################################################
###################      Functions    ###########################
#################################################################

def user_id_from_tg_id(tg_id) -> int:
    fields = [Users_tg.user_id]
    filters = [Users_tg.user_tg_id == tg_id]
    user_query = handler.execute_dynamic_query(fields=fields, filters=filters)
    user_id = user_query.scalar()
    return user_id

def exists(table, filters):
    result = handler.execute_dynamic_query(
        fields=[table],
        filters=filters
    )
    return result.first() is not None

#################################################################
#####################       API      ############################
#################################################################

def get_projects_by_user_id():
    params = handler.get_params('user_id', 'tg_id', request=request)
    if handler.check_data("user_id",data = params) and handler.check_data("tg_id",data = params):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400

    if params['tg_id']:  # Проверяем, что tg_id существует
        user_id = user_id_from_tg_id(params.get("tg_id"))
        if user_id:  # Если функция возвращает значение
            params['user_id'] = user_id
        else:
            return jsonify(handler.answer(False, "hasnt this tg", 2000)),404

    table = Projects

    fields = [
        table.id, table.title, table.description,table.status, table.start_date,table.head_id,
    ]

    joins = [
        (project_user, project_user.c.project_id == table.id, True)
    ]

    filters = [
        or_(
            table.head_id == params['user_id'],
            project_user.c.user_id == params['user_id']
        )
    ]

    def map_results(results):
        projects = []
        for row in results:
            project = {
                "id": row.id,
                "title": row.title,
                "status": row.status,
                "description": row.description,
                "start_date": row.start_date,
                "role": row.head_id == params['user_id']  # Если user_id является head, то роль True
            }
            projects.append(project)
        return projects

    try:
        res = handler.execute_dynamic_query(fields=fields,filters= filters,joins= joins,result_mapper= map_results)
        return jsonify(handler.answer(True, res, 1001)), 200
    except Exception as e:
        return jsonify(handler.answer(False, traceback.format_exc(), 2000)), 500

def get_user_tasks():
    params = handler.get_params('user_id', 'sprint_id', 'tg_id', request=request)

    if handler.check_data("user_id",data = params) and handler.check_data("tg_id",data = params) and handler.check_data("sprint_id",data = params):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400

    if params['tg_id']:  # Проверяем, что tg_id существует
        user_id = user_id_from_tg_id(params.get("tg_id"))
        if user_id:  # Если функция возвращает значение
            params['user_id'] = user_id
        else:
            return jsonify(handler.answer(False, "hasnt this tg", 2000)),404

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
    try:
        res = handler.execute_dynamic_query(fields=fields, filters=filters, joins=joins, result_mapper=map_results)
        return jsonify(handler.answer(True,res, 1001)),200
    except:
        return jsonify(handler.answer(False,"Error", 2000)),500

def get_sprints():
    params = handler.get_params('project_id', request=request)
    if handler.check_data("project_id",data = params):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400

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

        res = handler.execute_dynamic_query(fields=fields,filters= filters, result_mapper=map_results)
        return jsonify(handler.answer(True, res, 1001)), 200
    except Exception as e:
        return jsonify(handler.answer(False, {'mess':"error", 'exception':str(e)}, 2000)),404

def add_user():
    data = request.json
    if handler.check_data("login","password","email",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400
    filters = [
        or_(
            Users.login == data.get("login"),
            Users.email == data.get("email")
        )
    ]
    if exists(Users,filters):
        return jsonify(handler.answer(False,"User already exists", 2000)),400

    new_user = Users(
        login=data.get("login"),
        password_hash=generate_password_hash(data.get('password')),
        email=data.get("email")
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(handler.answer(True, "All good", 1001)),200
    except:
        return jsonify(handler.answer(False, "Error", 2000)), 500


def gen():
    data = request.json
    if handler.check_data("user_id","uniqueCode",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400

    filters = [
            TMP_code.user_id == data.get("user_id"),
    ]
    if exists(TMP_code,filters):
        return jsonify(handler.answer(False,{'mess':"Code already getted"}, 2000)),400
    if exists(Users_tg, [Users_tg.user_id == data.get("user_id")]):
        return jsonify(handler.answer(False,{'mess':"User already registred"}, 2000)),400
    new_tmp_code = TMP_code(
        user_id=data.get('user_id'),
        unic_code=data.get('uniqueCode')
    )
    try:
        db.session.add(new_tmp_code)
        db.session.commit()
        return jsonify(handler.answer(True, [], 1001)), 200
    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        return jsonify(handler.answer(False, "Error", 2000)), 500

def add_tg_user():
    data = request.json
    if handler.check_data("tg_id","uniqueCode",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400
    code = data.get("uniqueCode")
    tg_id = data.get("tg_id")

    is_code_exists = handler.execute_dynamic_query(
        fields=[TMP_code],
        filters=[TMP_code.unic_code == code]
    ).scalars().first()
    if not is_code_exists:
        return jsonify(handler.answer(False,{'mess':"Code not found"}, 2000)),404

    user_id = is_code_exists.user_id

    new_user_tg = Users_tg(
        user_id=user_id,
        user_tg_id=tg_id
    )

    try:
        db.session.delete(is_code_exists)
        db.session.add(new_user_tg)
        db.session.commit()
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        db.session.rollback()  # Откатываем изменения в случае ошибки
        return jsonify(handler.answer(False,{'mess':"Error", 'Error:':str(e)}, 2000)),500

def create_project():
    data = request.json
    if handler.check_data("user_id","project_title","project_description",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400

    new_project = Projects(
        title=data.get("project_title"),
        head_id=data.get("user_id"),
        description=data.get("project_description"),
        start_date= datetime.now()+ timedelta(hours=3),
        status= 1,
    )

    try:
        db.session.add(new_project)
        db.session.commit()
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        return jsonify(handler.answer(False,{'mess':"Error", 'Error:':str(e)}, 2000)),500

def create_sprint():
    data = request.json
    if handler.check_data("project_id","sprint_duration",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400
    new_sprint = Sprints(
        start_date=datetime.now()+ timedelta(hours=3),
        status=1,
        end_date=datetime.now()+ timedelta(hours=3) + timedelta(days=data.get("sprint_duration")),
        project_id=data.get("project_id")
    )
    try:
        db.session.add(new_sprint)
        db.session.commit()
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        return jsonify(handler.answer(False,{'mess':"Error", 'Error:':str(e)}, 2000)),500

def create_tag():
    data = request.json
    if handler.check_data("description","tag_name",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400
    new_tag = Tags(
        description= data.get("description"),
        tag_name=data.get("tag_name")
    )
    try:
        db.session.add(new_tag)
        db.session.commit()
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        return jsonify(handler.answer(False,{'mess':"Error", 'Error:':str(e)}, 2000)),500

def create_task():
    data = request.json
    if handler.check_data("user_id","task_description","name",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400

    is_have_duration =not handler.check_data("task_duration",data = data)
    is_have_tags =not handler.check_data("tags_ids",data = data)
    is_have_sprint =not handler.check_data("sprint_id",data = data)

    if not is_have_duration and is_have_sprint:
        data['task_duration']=handler.execute_dynamic_query(
                fields=[Sprints.end_date],
                filters=[Sprints.id == data.get("sprint_id")]
                ).scalars().first()

    elif not is_have_duration and not is_have_sprint:
        return jsonify(handler.answer(False, "error, need sprint_id or task_duration", 2000)),404

    new_task = Tasks(
        description=data.get("task_description"),
        task_name=data.get("name"),
        status = 1,
        set_time=datetime.now()+ timedelta(hours=3),
        end_time=data.get("task_duration") if not is_have_duration else datetime.now()+ timedelta(hours=3)+timedelta(days=data.get("task_duration")),
        user_id=data.get("user_id"),
        sprint_id=data.get('sprint_id') if is_have_sprint else None
    )

    if is_have_tags:
        tags = handler.execute_dynamic_query(
            fields=[Tags], filters=[Tags.id.in_(data.get("tags_ids"))]
        ).scalars().all()

        if not tags:
            return jsonify(handler.answer(False, "error, wrong tags", 2000)),404
        for tag in tags:
            new_task.tags.append(tag)  # Добавляем тег в задачу

    try:
        db.session.add(new_task)
        db.session.commit()
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        db.session.rollback()
        return jsonify(handler.answer(False,{'mess':"Error", 'Error:':str(e)}, 2000)),500

def add_user_to_project():
    data = request.json
    if handler.check_data("user_id","project_id",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400

    user = handler.execute_dynamic_query(
        fields=[Users],
        filters=[Users.id == data.get('user_id')]
    ).scalars().first()

    if not user:
        return jsonify(handler.answer(False, "error", 2009)),400

    project = handler.execute_dynamic_query(
        fields=[Projects],
        filters=[Projects.id == data.get('project_id')]
    ).scalars().first()

    if not project:
        return jsonify(handler.answer(False, "error", 2010)),400

    existing_member = handler.execute_dynamic_query(
        fields=[project_user],
        filters=[
            project_user.c.project_id == data.get('project_id'),
            project_user.c.user_id == data.get('user_id')
        ]
    ).scalars().first()

    if existing_member:
        return jsonify(handler.answer(False, "User already in project", 2000)),400

    try:
        new_member = project_user.insert().values(project_id=data.get('project_id'), user_id=data.get('user_id'))
        handler.db.session.execute(new_member)
        handler.db.session.commit()
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        db.session.rollback()
        return jsonify(handler.answer(False,{'mess':"Error", 'error:':str(e)}, 2011)),500


def is_user_exists():
    data = request.json
    if handler.check_data("login","password",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)", 'data':type(data)}, 2000)),400
    user = handler.execute_dynamic_query(fields=[Users],filters=[Users.login == data.get("login")]).scalars().first()
    return jsonify(
        handler.answer(
            Users.check_password(user, data.get("password")) if user else False,"Is_exists",1001
            )
        ), 200

def check_telegram_id():
    params = handler.get_params('tg_id', request=request)
    if handler.check_data("tg_id",data = params):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400
    return jsonify(
        handler.answer(
            exists(Users_tg,[Users_tg.user_tg_id == params.get("tg_id")]),"Is_exists",1001
            )
        ), 200


def change_task_status():
    params = handler.get_params('status',"task_id", request=request)
    if handler.check_data('status',"task_id",data = params) and not isinstance(params.get("status"), int):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),404

    task = db.session.query(Tasks).get(params.get("task_id"))

    if not task:
        jsonify(handler.answer(False, "error", 2000)),404
    try:
        task.status = params.get("status")
        db.session.commit()  # Сохраняем изменения в базе данных
    except:
        return jsonify(handler.answer(False, "error", 2000)),500
    return jsonify({"success": True, "code": 1001}), 200

def change_project_status_and_sprints():
    params = handler.get_params('status',"project_id", request=request)
    if handler.check_data('status',"project_id",data = params) and not isinstance(params.get("status"), int):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),404

    project = handler.execute_dynamic_query(
        fields=[Projects],
        filters=[Projects.id == params.get('project_id')]
        ).scalar_one_or_none()
    if not project:
        jsonify(handler.answer(False, "Hasnt this project_id", 2000)),404

    try:
        project.status = params.get('status')
        sprints = handler.execute_dynamic_query(
            fields=[Sprints],
            filters=[Sprints.project_id == params.get('project_id'), Sprints.status == 1]
            ).scalars().all()
        for sprint in sprints:
            sprint.status = 3  # Изменяем статус спринта на 3
            tasks = handler.execute_dynamic_query(
                fields=(Tasks), filters=(Tasks.sprint_id == sprint.id)
                ).scalars().all()
            for task in tasks:
                if task.status != 2:  # Если статус задачи не равен 2
                    task.status = 3  # Обновляем статус задачи на 3
        db.session.commit()  # Сохраняем изменения в базе данных
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        db.session.rollback()
        return jsonify(handler.answer(False,{'mess':"Error", 'error:':str(e)}, 2000)),500

def change_sprint_status():
    params = handler.get_params('status',"sprint_id", request=request)
    if handler.check_data('status',"sprint_id",data = params) and not isinstance(params.get("status"), int):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),404

    sprint = handler.execute_dynamic_query(
        fields=(Sprints), filters=(Sprints.id == params.get('sprint_id'))
        ).scalar_one_or_none()
    if not sprint:
        return jsonify(handler.answer(False,{'mess':"Dont have sprints with this id"}, 2000)),404
    try:
        sprint.status = params.get('status')
        tasks = handler.execute_dynamic_query(
            fields=(Tasks), filters=(Tasks.sprint_id == params.get('sprint_id'))
            ).scalars().all()
        for task in tasks:
            if task.status != 2:  # Если статус задачи не равен 2
                task.status = 3  # Обновляем статус задачи на 3
        db.session.commit()  # Сохраняем изменения в базе данных
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        db.session.rollback()
        return jsonify(handler.answer(False,{'mess':"Error", 'error:':str(e)}, 2000)),500




def delete_user_from_project():
    data = request.json
    if handler.check_data("user_to_delete_id","project_id",data = data):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),400
    user_to_delete_id = data.get("user_to_delete_id")
    project_id = data.get("project_id")

    pr_user = handler.execute_dynamic_query(
        fields=(project_user),
        filters=(
            project_user.c.user_id == user_to_delete_id,
            project_user.c.project_id == project_id
        )
    ).scalars().first()
    if not pr_user:
        return jsonify(handler.answer(False,{'mess':"havent this user in project"}, 2000)),404

    try:
        delete_query = delete(project_user).where(
            project_user.c.user_id == user_to_delete_id,
            project_user.c.project_id == project_id
        )
        db.session.execute(delete_query)
        db.session.commit()
        return jsonify(handler.answer(True,"All good", 1001)),200
    except Exception as e:
        db.session.rollback()
        return jsonify(handler.answer(False,{'mess':"Error", 'error:':str(e)}, 2000)),500


def users_in_project():
    params = handler.get_params('project_id', request=request)
    if handler.check_data('project_id',data = params):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),404

    fields = [
        project_user.c.user_id.label("user_id"),
        Users.login.label("username"),
        (project_user.c.user_id == Projects.head_id).label("role"),
    ]
    joins = [
        (Users, Users.id == project_user.c.user_id, False),
        (Projects, Projects.id == project_user.c.project_id, False)
    ]
    filters = [
        project_user.c.project_id == params['project_id'],
    ]
    def map_results(results):
        return [
            {
                "user_id": row.user_id,
                "username": row.username,
                "role": row.role
            }
            for row in results
        ]

    try:
        res = handler.execute_dynamic_query(fields=fields,filters=filters,joins=joins,result_mapper= map_results)
        project = handler.execute_dynamic_query(fields = [Projects.head_id], filters = [Projects.id == params['project_id']]).scalars().first()
        head_user = handler.execute_dynamic_query(fields = [Users.id, Users.login], filters = [Users.id == project])

        user = [{"user_id" :head.id,"username":head.login, "role":True} for head in head_user]
        res += user
        return jsonify(handler.answer(True, res, 1001)), 200
    except Exception as e:
        return jsonify(handler.answer(False, traceback.format_exc(), 2000)), 500

def get_user():
    """
    Получает поля login и email для пользователя по его user_id.
                            or
    Получает поле id и email пользователя по его login.
    """
    params = handler.get_params('user_id',"login", request=request)
    if handler.check_data('user_id',data = params) and handler.check_data('login',data = params):
        return jsonify(handler.answer(False,{'mess':"Miss parametr(s)"}, 2000)),404

    def map_results(results):
        # Преобразуем результат запроса в словарь
        result = results.fetchone()
        if result:
            return {
                "id":result.user_id,
                "login": result.login,
                "email": result.email
            }
        return None
    try:
        user = handler.execute_dynamic_query(
        fields=[Users.id.label("user_id"),Users.login.label("login"), Users.email.label("email")],
        filters=[or_(
            Users.id == params.get("user_id"),
            Users.login == params.get("login"))],
        result_mapper=map_results
        )
        if user is not None:
            return jsonify(handler.answer(True,user,1001)),200
        else:
            return jsonify(handler.answer(False, "User not found", 2000)),404
    except Exception as e:
        return jsonify(handler.answer(False,{"Exception" : str(e)}, 2000)),500
