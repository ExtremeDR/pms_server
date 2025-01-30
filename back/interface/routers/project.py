from flask import Blueprint, jsonify, request
from back.services.validation import check_data, get_params, obj_to_dict
from back.services.controller.project_controller import ProjectController
from back.services.werification_token import token_required
from back.infrastructure.database import db


router = Blueprint('project', __name__, url_prefix='/project')
controller = ProjectController(db)

@router.route('/get/<id>', methods=['GET'])
@token_required
def get_id(self, id):
    """
    Получает проект по ID.
    ---
    tags:
      - Projects
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID проекта, который нужно получить.
    responses:
      200:
        description: Данные проекта.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                title:
                  type: string
                  example: "Project Title"
                description:
                  type: string
                  example: "Project Description"
                status:
                  type: integer
                  example: 1
                start_date:
                  type: string
                  example: "2025-01-30T12:00:00"
      404:
        description: Проект не найден.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Project not found"
            code:
              type: integer
              example: 2001
    """
    param = id
    project = self.service.get(param)

    # Преобразуем объект проекта в словарь
    data = obj_to_dict(project)

    return jsonify(data), 200

@router.route('/get-projects-for-user', methods=['GET'])
@token_required
def get_projects_for_user():
    """
    Получает проекты, связанные с пользователем.
    ---
    tags:
      - Projects
    parameters:
      - name: user_id
        in: query
        type: integer
        required: true
        description: ID пользователя.
      - name: tg_id
        in: query
        type: integer
        required: false
        description: Telegram ID пользователя.
    responses:
      200:
        description: Список проектов пользователя.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "Project Title"
                  description:
                    type: string
                    example: "Project Description"
                  status:
                    type: integer
                    example: 1
      400:
        description: Неверный запрос.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Missing parameters"
            code:
              type: integer
              example: 2000
    """
    params = get_params('user_id', 'tg_id', request=request)
    if check_data("user_id", data=params) and check_data("tg_id", data=params):
        return jsonify({False, {'mess': "Miss parameter(s)"}, 2000}), 400

    if params['tg_id']:  # Проверяем, что tg_id существует
        user_id = controller.user_id_from_tg_id(params.get("tg_id"))
        if user_id:  # Если функция возвращает значение
            params['user_id'] = user_id
        else:
            return jsonify({False, "hasn't this tg", 2000}), 404

    try:
        # Используем контроллер для получения проектов
        projects = controller.get_projects_by_user_id(params['user_id'])
        return jsonify({True, projects, 1001}), 200
    except Exception as e:
        return jsonify({False, {'mess': "Error", 'error': str(e)}, 2000}), 500

@router.route('/get-head-id', methods=['GET'])
@token_required
def get_head_id(self):
    """
    Получение ID главы проекта по ID проекта.
    ---
    tags:
      - Projects
    parameters:
      - name: project_id
        in: query
        type: integer
        required: true
        description: ID проекта для получения главы проекта.
    responses:
      200:
        description: ID главы проекта успешно получен.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            head_id:
              type: integer
              example: 1
            code:
              type: integer
              example: 1001
      404:
        description: Проект не найден.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Project not found"
            code:
              type: integer
              example: 2000
      500:
        description: Ошибка сервера.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Error"
            code:
              type: integer
              example: 2000
    """
    project_id = request.args.get('project_id')

    if not project_id:
        return jsonify({'success': False, 'message': "Missing project_id", 'code': 2000}), 400

    response, status_code = controller.get_head_id_by_project_id(project_id)
    return jsonify(response), status_code

@router.route('/post', methods=['POST'])
@token_required
def post(self):
    """
    Создание нового проекта.
    ---
    tags:
      - Projects
    parameters:
      - name: project_title
        in: body
        type: string
        required: true
        description: Название проекта.
      - name: project_description
        in: body
        type: string
        required: true
        description: Описание проекта.
      - name: user_id
        in: body
        type: integer
        required: true
        description: ID пользователя, который будет главой проекта.
    responses:
      200:
        description: Проект успешно создан.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "All good"
            code:
              type: integer
              example: 1001
      400:
        description: Ошибка в параметрах запроса.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Miss parameter(s)"
            code:
              type: integer
              example: 2000
      500:
        description: Ошибка сервера.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Error"
            code:
              type: integer
              example: 2000
    """
    data = request.json
    response, status_code = controller.create_project(data)
    return jsonify(response), status_code

@router.route('/change-status', methods=['POST'])
@token_required
def set_status(self):
    """
    Изменение статуса проекта и его спринтов.
    ---
    tags:
      - Projects
    parameters:
      - name: project_id
        in: body
        type: integer
        required: true
        description: ID проекта, для которого нужно изменить статус.
      - name: status
        in: body
        type: integer
        required: true
        description: Новый статус проекта.
    responses:
      200:
        description: Статус проекта и спринтов успешно обновлен.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Status updated successfully"
            code:
              type: integer
              example: 1001
      400:
        description: Ошибка параметров запроса.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Missing parameters or invalid status"
            code:
              type: integer
              example: 2000
      404:
        description: Проект не найден.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Project not found"
            code:
              type: integer
              example: 2000
      500:
        description: Ошибка сервера.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Error"
            code:
              type: integer
              example: 2000
    """
    data = request.json
    status = data.get('status')
    project_id = data.get('project_id')

    if not status or not project_id:
        return jsonify({'success': False, 'message': "Missing status or project_id", 'code': 2000}), 400

    response, status_code = controller.change_project_status_and_sprints(status, project_id)
    return jsonify(response), status_code

@router.route('/users-in-project', methods=['POST'])
@token_required
def get_users_in_project(self):
    """
    Получение списка пользователей в проекте, включая главу проекта.
    ---
    tags:
      - Projects
    parameters:
      - name: project_id
        in: body
        type: integer
        required: true
        description: ID проекта, для которого нужно получить пользователей.
    responses:
      200:
        description: Список пользователей проекта успешно получен.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  user_id:
                    type: integer
                    example: 1
                  username:
                    type: string
                    example: "user1"
                  role:
                    type: boolean
                    example: true
              example: [
                {"user_id": 1, "username": "admin", "role": true},
                {"user_id": 2, "username": "user1", "role": false}
              ]
            code:
              type: integer
              example: 1001
      404:
        description: Oтсутствует project_id или проект не найден.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Missing project_id"
            code:
              type: integer
              example: 2000
      500:
        description: Ошибка сервера.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Error"
            code:
              type: integer
              example: 2000
    """
    data = request.json
    project_id = data.get('project_id')

    if not project_id:
        return jsonify({'success': False, 'message': "Missing project_id", 'code': 2000}), 404

    response, status_code = self.controller.get_users_in_project(project_id)
    return jsonify(response), status_code
