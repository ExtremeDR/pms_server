from sqlalchemy import select

class Request():
    def __init__(self, db) -> None:
        self.db =db

    def get_params(*params, request):
        """
        Получает указанные параметры из request.args.

        :param params: Имена параметров, которые нужно получить.
        :return: Словарь с указанными параметрами и их значениями.
        """
        result = {param: request.args.get(param) for param in params}
        return result

    def check_data(*params:str, data:dict):
        """
        Проверяет наличие всех переданных параметров в словаре data.

        :param params: Параметры, которые нужно проверить.
        :param data: Словарь данных, в котором проверяются параметры.
        :return: True, если все параметры есть в data, иначе False.
        """
        for param in params:
            if param not in data:  # Проверка наличия параметра в data
                return False
        return True

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