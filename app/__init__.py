from flask import Flask, render_template
from .config import Config
from .db_second import init_db,  db, migrate
from app.api.werification_token import token_required
import app.api.endpoints as API
from datetime import datetime, timedelta


def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        init_db()  

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/add-user', methods=['POST'])#
    @token_required
    def add_user():
        return API.add_user()

    @app.route('/generate-code', methods=['POST'])#
    @token_required
    def gen():
        return API.gen()

    @app.route('/add-tg-user', methods=['POST'])#
    @token_required
    def add_tg_user():
        return API.add_tg_user()

    @app.route('/is-user-exists', methods=['POST'])#
    @token_required
    def is_user_exists():
        return API.is_user_exists()

    @app.route('/check_telegram_id', methods=['GET'])#
    @token_required
    def check_telegram_id():
        return API.check_telegram_id()

    @app.route('/create_project', methods=['POST'])
    @token_required
    def create_project():
        return API.create_project()

    @app.route('/create_task', methods=['POST'])
    @token_required
    def create_task():
        return API.create_task()

    @app.route('/change_task_status', methods=['PATCH', 'GET'])
    @token_required
    def change_task_status():
        return API.change_task_status()

    @app.route('/change_project_status_and_sprints', methods=['PATCH', 'GET'])
    @token_required
    def change_project_status_and_sprints():
        return API.change_project_status_and_sprints()

    @app.route('/change_sprint_status', methods=['PATCH', 'GET'])
    @token_required
    def change_sprint_status():
        return API.change_sprint_status()

    @app.route('/create_sprint', methods=['POST'])
    @token_required
    def create_sprint():
        return API.create_sprint()

    @app.route('/create_tag', methods=['POST'])
    @token_required
    def create_tag():
        return API.create_tag()

    @app.route('/all_projects', methods=['GET'])#
    @token_required
    def all_projects():
        return API.get_projects_by_user_id()

    @app.route('/all_tasks', methods=['GET'])#
    @token_required
    def all_tasks_by_user_id_or_tg_id():
        return API.get_user_tasks()

    @app.route('/sprints_by_project_id', methods=['GET'])#
    @token_required
    def sprints_by_project_id():
        return API.get_sprints()

    # # @app.route('/users_in_project', methods=['GET'])
    # # @token_required
    # # def users_in_project():
    # #     return API.users_in_project()

    @app.route('/add_user_to_project', methods=['POST'])
    @token_required
    def add_user_to_project():
        return API.add_user_to_project()

    @app.route('/delete_user_from_project', methods=['DELETE'])
    @token_required
    def delete_user_from_project():
        return API.delete_user_from_project()
    
    return app