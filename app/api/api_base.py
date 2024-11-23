from functools import wraps
import jwt
from flask import jsonify, request
from app.config import Config as cf
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            decoded = jwt.decode(token, cf.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403
        return f(*args, **kwargs)
    return decorated





class APIClient:

    def __init__(self, db, config):
        self.db = db
        self.config = config

    def execute_query(self, query):
        try:
            #return self.db.session.execute(query).scalars().all()
            return self.db.session.execute(query).fetchall()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_datas(*params):
        """
        Получает указанные параметры из request.args.

        :param params: Имена параметров, которые нужно получить.
        :return: Словарь с указанными параметрами и их значениями.
        """
        result = {param: (request.json).get(param) for param in params}
        return result

    def get_params(*params, request):
        """
        Получает указанные параметры из request.args.

        :param params: Имена параметров, которые нужно получить.
        :return: Словарь с указанными параметрами и их значениями.
        """
        result = {param: request.args.get(param) for param in params}
        return result

    def to_json(self, data, message="Success", code=1001):
        if data:
            return jsonify({"data": data, "message": message, "code": code}), 200
        return jsonify({"data": [], "message": "Error - empty data", "code": 2000}), 404