from flask import Blueprint, jsonify, request
from back.infrastructure.database import db
from back.services.validation import check_data, get_params, obj_to_dict
from back.services.controller.tg_service import TelegramUserController
from back.services.werification_token import token_required

router = Blueprint('tg', __name__, url_prefix='/tg')
controller = TelegramUserController()

@router.route('/gen-code', methods=['POST'])
@token_required
def generate_code():
    """
    Генерация уникального кода для пользователя.
    ---
    tags:
      - Telegram
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              description: ID пользователя.
              example: 1
            uniqueCode:
              type: string
              description: Уникальный код для привязки.
              example: "ABC123"
    responses:
      200:
        description: Код успешно сгенерирован.
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            code:
              type: integer
      400:
        description: Проблема с данными запроса.
      500:
        description: Ошибка на сервере.
    """
    data = request.json
    if check_data("user_id", "uniqueCode", data=data):
        return jsonify({False, {'mess': "Missing parameter(s)"}, 2000}), 400

    user_id = data.get("user_id")
    unique_code = data.get("uniqueCode")
    response, status = controller.generate_code(user_id, unique_code)
    return jsonify(response), status


@router.route('/add-tg', methods=['POST'])
@token_required
def add_tg_user():
    """
    Привязка Telegram ID к пользователю.
    ---
    tags:
      - Telegram
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            tg_id:
              type: integer
              description: Telegram ID пользователя.
              example: 123456789
            uniqueCode:
              type: string
              description: Уникальный код для подтверждения.
              example: "ABC123"
    responses:
      200:
        description: Пользователь успешно привязан.
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            code:
              type: integer
      400:
        description: Проблема с данными запроса.
      404:
        description: Код не найден.
      500:
        description: Ошибка на сервере.
    """
    data = request.json
    if check_data("tg_id", "uniqueCode", data=data):
        return jsonify({False, {'mess': "Missing parameter(s)"}, 2000}), 400

    tg_id = data.get("tg_id")
    unique_code = data.get("uniqueCode")
    response, status = controller.add_telegram_user(tg_id, unique_code)
    return jsonify(response), status


@router.route('/check-tg', methods=['GET'])
@token_required
def check_tg_user():
    """
    Проверка наличия Telegram ID в базе данных.
    ---
    tags:
      - Telegram
    parameters:
      - name: tg_id
        in: query
        required: true
        type: integer
        description: Telegram ID пользователя.
        example: 123456789
    responses:
      200:
        description: Успешная проверка.
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            exists:
              type: boolean
            code:
              type: integer
      400:
        description: Проблема с параметром запроса.
    """
    tg_id = request.args.get("tg_id")
    if not tg_id:
        return jsonify({False, {'mess': "Missing parameter(s)"}, 2000}), 400

    response, status = controller.check_telegram_id(tg_id)
    return jsonify(response), status