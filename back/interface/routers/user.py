from flask import Blueprint, jsonify, request
from back.infrastructure.database import db
from back.services.validation import check_data, get_params, obj_to_dict
from back.services.controller.user_service import UserService
from back.services.werification_token import token_required

router = Blueprint('user', __name__, url_prefix='/user')


controller = UserService(db)
    
@router.route('/get/<login>', methods=['GET'])
@token_required
def get_user_by_login(login):
    """
    Получает пользователя по его логину.
    ---
    tags:
      - Users
    parameters:
      - name: login
        in: path
        required: true
        type: string
        description: Логин пользователя.
        example: "user123"
    responses:
      200:
        description: Пользователь найден.
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
                login:
                  type: string
                  example: "user123"
                email:
                  type: string
                  example: "user@example.com"
      404:
        description: Пользователь не найден.
      500:
        description: Ошибка на сервере.
    """
    user = controller.get_user_by_login(login)
    if user:
        data = obj_to_dict(user, ["id", "login", "email"])
        return jsonify({"success": True, "data": data}), 200
    return jsonify({"success": False, "message": "User not found", "code": 2000}), 404


@router.route('/get/<id>', methods=['GET'])
@token_required
def get_user_by_id(id):
    """
    Получает пользователя по его ID.
    ---
    tags:
      - Users
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: ID пользователя.
        example: 1
    responses:
      200:
        description: Пользователь найден.
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
                login:
                  type: string
                  example: "user123"
                email:
                  type: string
                  example: "user@example.com"
      404:
        description: Пользователь не найден.
      500:
        description: Ошибка на сервере.
    """
    user = controller.get_user_by_id(id)
    if user:
        data = obj_to_dict(user, ["id", "login", "email"])
        return jsonify({"success": True, "data": data}), 200
    return jsonify({"success": False, "message": "User not found", "code": 2000}), 404


@router.route('/create', methods=['POST'])
@token_required
def post():
    """
    Создаёт нового пользователя.
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            login:
              type: string
              description: Логин пользователя.
              example: "user123"
            password:
              type: string
              description: Пароль пользователя.
              example: "password123"
            email:
              type: string
              description: Электронная почта пользователя.
              example: "user@example.com"
    responses:
      200:
        description: Пользователь успешно создан.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "All good"
      400:
        description: Ошибка в данных запроса.
      500:
        description: Ошибка на сервере.
    """
    data = request.json
    response, status = controller.create_user(data)
    return jsonify(response), status

@router.route('/delete', methods=['DELETE'])
@token_required
def delete_user():
    """
    Удаляет пользователя по ID.
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: query
        required: true
        type: integer
        description: ID пользователя.
        example: 1
    responses:
      200:
        description: Пользователь успешно удалён.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "User deleted successfully."
      400:
        description: Отсутствует обязательный параметр user_id.
      404:
        description: Пользователь не найден.
      500:
        description: Ошибка на сервере.
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Missing user_id", "code": 2000}), 400
    response, status = controller.delete_user(user_id)
    return jsonify(response), status

@router.route('/add-to-project', methods=['POST'])
@token_required
def add_user_to_project():
    """
    Добавляет пользователя в проект.
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: body
        type: integer
        required: true
        description: ID пользователя, которого нужно добавить в проект.
      - name: project_id
        in: body
        type: integer
        required: true
        description: ID проекта, в который нужно добавить пользователя.
    responses:
      200:
        description: Пользователь успешно добавлен в проект.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "User added to project"
            code:
              type: integer
              example: 1001
      400:
        description: Ошибка при добавлении пользователя в проект.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "User already in project"
            code:
              type: integer
              example: 2000
      404:
        description: Не найден пользователь или проект.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "User not found"
            code:
              type: integer
              example: 2009
      500:
        description: Ошибка на сервере.
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
              example: 2011
    """
    data = request.json
    response, status = controller.add_user_to_project(data)
    return jsonify(response), status


@router.route('/remove-from-project', methods=['POST'])
@token_required
def remove_user_from_project():
    """
    Удаляет пользователя из проекта.
    ---
    tags:
      - Users
    parameters:
      - name: user_to_delete_id
        in: body
        type: integer
        required: true
        description: ID пользователя, которого нужно удалить из проекта.
      - name: project_id
        in: body
        type: integer
        required: true
        description: ID проекта, из которого нужно удалить пользователя.
    responses:
      200:
        description: Пользователь успешно удален из проекта.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "User removed from project"
            code:
              type: integer
              example: 1001
      400:
        description: Ошибка при удалении пользователя из проекта.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "User not found in project"
            code:
              type: integer
              example: 2000
      404:
        description: Не найден пользователь или проект.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "User not found in project"
            code:
              type: integer
              example: 2000
      500:
        description: Ошибка на сервере.
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
    response, status = controller.remove_user_from_project(data)
    return jsonify(response), status