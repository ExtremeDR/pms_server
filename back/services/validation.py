def get_params(self,*params, request):
    """
    Получает указанные параметры из request.args.

    :param params: Имена параметров, которые нужно получить.
    :return: Словарь с указанными параметрами и их значениями.
    result = {param: request.args.get(param) for param in params if request.args.get(param) is not None}
    """
    result = {param: request.args.get(param) for param in params if request.args.get(param) is not None}
    return result

def check_data(self,*params, data:dict) -> bool:
    """
    Проверяет наличие всех переданных параметров в словаре data.

    :param params: Параметры, которые нужно проверить.
    :param data: Словарь данных, в котором проверяются параметры.
    :return: False, если все параметры есть в data, иначе True.
    """
    for p in params:
        if p not in data:
            return True
    return False

from sqlalchemy import inspect

def obj_to_dict(obj, keys=None):
    # Получаем все доступные ключи (колонки)
    all_columns = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

    # Если список ключей не передан, возвращаем все колонки
    if keys is None:
        return all_columns

    # Создаем словарь только с указанными ключами
    return {key: all_columns[key] for key in keys if key in all_columns}