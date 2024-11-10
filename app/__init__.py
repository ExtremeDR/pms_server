from flask import Flask, render_template
import app.config as config
from config import Config
from sqlalchemy import select
#from db import init_db, Users_tg, Users, TMP_code,  db
from app.db_second import init_db,  db
import app.handlers as hdl

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app) 


    with app.app_context():
        init_db()  # Инициализируем базу данных

    # Главная страница
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/add-user/<secret_code>', methods=['POST'])
    def add_user(secret_code):
        return hdl._add_user(secret_code)
    
    @app.route('/generate-code/<secret_code>', methods=['GET'])
    def gen(secret_code):
        return hdl._gen(secret_code)
    
    @app.route('/add-tg-user/<secret_code>', methods=['POST'])
    def add_tg_user(secret_code):
        return hdl._add_tg_user(secret_code)
        
    @app.route('/is-user-exists/<secret_code>', methods=['GET'])
    def is_user_exists(secret_code):
        return hdl._is_user_exists(secret_code)
    
    @app.route('/check_telegram_id/<secret_code>', methods=['GET'])
    def check_telegram_id(secret_code):
        return hdl._check_telegram_id(secret_code)

    @app.route('/create_project/<secret_code>', methods=['POST'])
    def create_project(secret_code):
        return hdl._create_project(secret_code)
    
    @app.route('/create_task/<secret_code>', methods=['POST'])
    def create_task(secret_code):
        return hdl._create_task(secret_code)
        
    @app.route('/change_task_status/<secret_code>', methods=['PATCH'])
    def change_task_status(secret_code):
        return hdl._change_task_status(secret_code)
        
    @app.route('/create_sprint/<secret_code>', methods=['POST'])
    def create_sprint(secret_code):
        return hdl._create_sprint(secret_code)
    
    @app.route('/create_tag/<secret_code>', methods=['POST'])
    def create_tag(secret_code):
        return hdl._create_tag(secret_code)
        
    @app.route('/create_task_from_other_task/<secret_code>', methods=['POST'])
    def create_task_from_other_task(secret_code):
        return hdl._create_task_from_other_task(secret_code)
    
    @app.route('/all_projects_by_login/<secret_code>', methods=['POST'])
    def all_projects_by_login(secret_code):
        return hdl. _all_projects_by_login(secret_code)
    
    @app.route('/projects_by_head_id/<secret_code>', methods=['GET'])
    def projects_by_head_id(secret_code):
        return hdl._projects_by_head_id(secret_code)
    
    @app.route('/sprints_by_project_id/<secret_code>', methods=['GET'])
    def sprints_by_project_id(secret_code):
        return hdl._sprints_by_project_id(secret_code)
    
    @app.route('/tasks_by_sprint_id/<secret_code>', methods=['GET'])
    def tasks_by_sprint_id(secret_code):
        return hdl._tasks_by_sprint_id(secret_code)
        
    @app.route('/users_in_project/<secret_code>', methods=['GET'])
    def users_in_project(secret_code):
        return hdl._users_in_project(secret_code)
        
    @app.route('/add_user_to_project/<secret_code>', methods=['POST'])
    def add_user_to_project(secret_code):
        return hdl._add_user_to_project(secret_code)
            
    @app.route('/delete_user_from_project/<secret_code>', methods=['DELETE'])
    def delete_user_from_project(secret_code):
        return hdl._delete_user_from_project(secret_code)
    return app

# if __name__ == '__main__':
#     app = create_app() 
#     #app.run(debug=True)
#     app.run(host="0.0.0.0", port=5000, debug=True)