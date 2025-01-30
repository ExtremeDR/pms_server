from flask import Blueprint, jsonify, request
from flasgger import swag_from
from back.services.controller.sprint_controller import SprintController
from back.services.werification_token import token_required
from back.infrastructure.database import db


router = Blueprint('sprint', __name__, url_prefix='/sprint')
controller = SprintController(db)


@router.route('/get', methods=['GET'])
@swag_from({
    'tags': ['Sprints'],
    'summary': 'Получение списка спринтов для проекта',
    'parameters': [
        {
            'name': 'project_id',
            'in': 'query',
            'type': 'integer',
            'description': 'ID проекта для получения спринтов',
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Список спринтов проекта успешно получен',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'start_date': {'type': 'string', 'format': 'date-time'},
                                'end_date': {'type': 'string', 'format': 'date-time'},
                                'status': {'type': 'integer'}
                            }
                        }
                    },
                    'code': {'type': 'integer'}
                }
            }
        },
        '400': {
            'description': 'Ошибка: Не передан обязательный параметр project_id'
        },
        '404': {
            'description': 'Ошибка: Проект с таким project_id не найден'
        }
    }
})
def get_sprints_route():
    """
    Получение списка спринтов для проекта по project_id.
    """
    params = request.args
    project_id = params.get('project_id')

    if not project_id:
        return jsonify({'success': False, 'message': 'Miss parametr(s)', 'code': 2000}), 400

    response, status_code = controller.get_sprints(project_id)
    return jsonify(response), status_code


@router.route('/post', methods=['POST'])
@token_required
@swag_from({
    'tags': ['Sprints'],
    'summary': 'Создание нового спринта',
    'parameters': [
        {
            'name': 'project_id',
            'in': 'body',
            'type': 'integer',
            'description': 'ID проекта, для которого создается спринт',
            'required': True
        },
        {
            'name': 'sprint_duration',
            'in': 'body',
            'type': 'integer',
            'description': 'Продолжительность спринта в днях',
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Спринт успешно создан',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'code': {'type': 'integer'}
                }
            }
        },
        '400': {
            'description': 'Ошибка: Не переданы обязательные параметры project_id или sprint_duration'
        },
        '500': {
            'description': 'Ошибка на сервере при создании спринта'
        }
    }
})
def create_sprint_route():
    """
    Создание нового спринта.
    """
    data = request.json
    project_id = data.get('project_id')
    sprint_duration = data.get('sprint_duration')

    if not project_id or not sprint_duration:
        return jsonify({'success': False, 'message': 'Miss parametr(s)', 'code': 2000}), 400

    response, status_code = controller.create_sprint(project_id, sprint_duration)
    return jsonify(response), status_code


@router.route('/status', methods=['PUT'])
@token_required
@swag_from({
    'tags': ['Sprints'],
    'summary': 'Обновление статуса спринта',
    'parameters': [
        {
            'name': 'sprint_id',
            'in': 'body',
            'type': 'integer',
            'description': 'ID спринта для обновления статуса',
            'required': True
        },
        {
            'name': 'status',
            'in': 'body',
            'type': 'integer',
            'description': 'Новый статус спринта',
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Статус спринта успешно обновлен',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'code': {'type': 'integer'}
                }
            }
        },
        '400': {
            'description': 'Ошибка: Не переданы обязательные параметры sprint_id или status'
        },
        '404': {
            'description': 'Ошибка: Спринт с таким ID не найден'
        },
        '500': {
            'description': 'Ошибка на сервере при обновлении статуса'
        }
    }
})
def update_sprint_status_route():
    """
    Обновление статуса спринта.
    """
    data = request.json
    sprint_id = data.get('sprint_id')
    new_status = data.get('status')

    if not sprint_id or new_status is None:
        return jsonify({'success': False, 'message': 'Miss parametr(s)', 'code': 2000}), 400

    response, status_code = controller.update_sprint_status(sprint_id, new_status)
    return jsonify(response), status_code