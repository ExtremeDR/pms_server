from flask import Flask, render_template, request,jsonify
from .config import Config
from .db_second import init_db,  db, migrate
from app.api.api_base import token_required
import app.api.creating_api as postApi
import app.api.deleting_api as deleteApi
import app.api.updating_api as updateApi
import app.api.endpoints as API
import app.api.get_api as getApi
from datetime import datetime, timedelta




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
    db.init_app(app)
    migrate.init_app(app, db)


    with app.app_context():
        init_db()  # Инициализируем базу данных

    # Главная страница
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/add-user', methods=['POST'])
    @token_required
    def add_user():
        return postApi._add_user()

    @app.route('/generate-code', methods=['POST'])
    @token_required
    def gen():
        return postApi._gen()

    @app.route('/add-tg-user', methods=['POST'])
    @token_required
    def add_tg_user():
        return postApi._add_tg_user()

    @app.route('/is-user-exists', methods=['POST'])
    @token_required
    def is_user_exists():
        return getApi._is_user_exists()

    @app.route('/check_telegram_id', methods=['POST'])
    @token_required
    def check_telegram_id():
        return getApi._check_telegram_id()

    @app.route('/create_project', methods=['POST'])
    @token_required
    def create_project():
        return postApi._create_project()

    @app.route('/create_task', methods=['POST'])
    @token_required
    def create_task():
        return postApi._create_task()

    @app.route('/change_task_status', methods=['PATCH'])
    @token_required
    def change_task_status():
        return updateApi._change_task_status()

    @app.route('/create_sprint', methods=['POST'])
    @token_required
    def create_sprint():
        return postApi._create_sprint()

    @app.route('/create_tag', methods=['POST'])
    @token_required
    def create_tag():
        return postApi._create_tag()

    @app.route('/create_task_from_other_task', methods=['POST'])
    @token_required
    def create_task_from_other_task():
        return postApi._create_task_from_other_task()

    @app.route('/all_projects', methods=['GET'])
    @token_required
    def all_projects():
        return API._all_projects_by_tg_id_or_user_id()

    # @app.route('/all_projects_by_tg_id/<secret_code>', methods=['GET'])
    # @token_required
    # def all_projects_by_tg_id(secret_code):
    #     params = request.args.get('user_id','tg_id')
    #     return getApi._all_projects_by_tg_id(secret_code)

    @app.route('/all_tasks', methods=['GET'])
    @token_required
    def all_tasks_by_user_id_or_tg_id():
        return API._tasks()

    # @app.route('/projects_by_head_id/<>', methods=['POST'])
    # @token_required
    # def projects_by_head_id():
    #     return getApi._projects_by_head_id()

    @app.route('/sprints_by_project_id', methods=['GET'])
    @token_required
    def sprints_by_project_id():
        return API._sprints_by_project_id()

    # @app.route('/tasks_by_sprint_id/<>', methods=['GET'])
    # @token_required
    # def tasks_by_sprint_id():
    #     return getApi._tasks_by_sprint_id()

    @app.route('/users_in_project', methods=['GET'])
    @token_required
    def users_in_project():
        return API._users_in_project()

    @app.route('/add_user_to_project', methods=['POST'])
    @token_required
    def add_user_to_project():
        return postApi._add_user_to_project()

    @app.route('/delete_user_from_project', methods=['DELETE'])
    @token_required
    def delete_user_from_project():
        return deleteApi._delete_user_from_project()
    return app

# if __name__ == '__main__':
#     app = create_app()
#     #app.run(debug=True)
#     app.run(host="0.0.0.0", port=5000, debug=True)