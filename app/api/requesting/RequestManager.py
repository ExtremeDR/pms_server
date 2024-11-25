from sqlalchemy import select

class Request():
    def __init__(self, db) -> None:
        self.db =db

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

    def execute_dynamic_query(self, fields, filters=None, joins=None, result_mapper=None):
        """
        Выполняет запрос к базе данных с параметрами:
        - fields: список полей для выборки.
        - filters: список фильтров (опционально).
        - joins: список джойнов (опционально).
        - result_mapper: функция для обработки результата (опционально).
        """
        query = select(*fields)

        if joins:
            for join_table, condition, is_outer in joins:
                query = query.join(join_table, condition, isouter=is_outer)

        if filters:
            for condition in filters:
                query = query.where(condition)

        results = self.db.session.execute(query)

        if result_mapper:
            return result_mapper(results)

        return results

    def answer(self,good:bool, data, code:int):
        return {'Success' : good, 'data':data, 'code':code}