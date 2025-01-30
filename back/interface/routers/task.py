from flask import Blueprint, jsonify, request
from back.services.validation import check_data, get_params, obj_to_dict
from back.services.controller.task_controller import TaskController
from back.services.werification_token import token_required

router = Blueprint('task', __name__, url_prefix='/task')
controller = TaskController()

@router.route('', methods=['POST'])
@token_required
def get_user_tasks_route(self):
    """
    Получение задач пользователя для указанного спринта и tg_id.
    ---
    tags:
      - Tasks
    parameters:
      - name: user_id
        in: body
        type: integer
        required: false
        description: ID пользователя.
      - name: sprint_id
        in: body
        type: integer
        required: false
        description: ID спринта.
      - name: tg_id
        in: body
        type: string
        required: false
        description: Telegram ID пользователя.
    responses:
      200:
        description: Список задач пользователя успешно получен.
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
                  task_name:
                    type: string
                    example: "Task 1"
                  description:
                    type: string
                    example: "Task description"
                  tags:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: integer
                          example: 1
                        name:
                          type: string
                          example: "Tag 1"
              example: [
                {"id": 1, "task_name": "Task 1", "description": "Description of task", "tags": [{"id": 1, "name": "Tag1"}]}
              ]
            code:
              type: integer
              example: 1001
      404:
        description: Ошибка: не найден tg_id или пользователь.
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "hasnt this tg"
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
    user_id = data.get('user_id')
    sprint_id = data.get('sprint_id')
    tg_id = data.get('tg_id')

    if not user_id and not tg_id:
        return jsonify({'success': False, 'message': "Miss parametr(s)", 'code': 2000}), 400

    response, status_code = controller.get_user_tasks(user_id=user_id, sprint_id=sprint_id, tg_id=tg_id)
    return jsonify(response), status_code