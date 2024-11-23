import abc

from sqlalchemy import select
class IRequest(abc.ABC):
    @abc.abstractmethod
    def get_data():
        pass
    
    @abc.abstractmethod
    def query():
        pass
    
    @abc.abstractmethod
    def answer():
        pass

class GetRequest(IRequest):
    def __init__(self) -> None:
        super().__init__()
    def get_params(*params, request):
        """
        Получает указанные параметры из request.args.

        :param params: Имена параметров, которые нужно получить.
        :return: Словарь с указанными параметрами и их значениями.
        """
        result = {param: request.args.get(param) for param in params}
        return result
    def execute_dynamic_query(self, table, fields, filters=None, joins=None, result_mapper=None):
        """
        Выполняет запрос к базе данных с параметрами:
        - table: таблица, с которой идет запрос.
        - fields: список полей для выборки.
        - filters: список фильтров (опционально).
        - joins: список джойнов (опционально).
        - result_mapper: функция для обработки результата (опционально).
        """
        query = select(*fields)

        # Добавление таблицы
        if joins:
            for join_table, condition, is_outer in joins:
                query = query.join(join_table, condition, isouter=is_outer)

        # Применение фильтров
        if filters:
            for condition in filters:
                query = query.where(condition)

        # Выполнение запроса
        results = self.api.execute_query(query)

        # Преобразование результата
        if result_mapper:
            return result_mapper(results)

        return results
    
    def answer(good:bool, data, code:int):
        return {'Success' : good, 'data':data, 'code':code}
