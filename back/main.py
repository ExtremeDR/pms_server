import logging
from flask import Flask
from .config import Config
from flasgger import Swagger
from back.interface.base import router


def create_app():

    # Настройка логгера
    logging.basicConfig(
        level=logging.DEBUG,  # Уровень логгирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат сообщения
        filename="app.log",  # Запись логов в файл (если нужно)
        filemode="a",  # Режим добавления в файл (a - append, w - overwrite)
    )


    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
    # db.init_app(app)
    # migrate.init_app(app, db)
    app.debug = True
    # with app.app_context():
    #     init_db()
    app.register_blueprint(router)
    swagger = Swagger(app)
    return app