from sqlalchemy import or_
from back.infrastructure.repositories.sqlalchemy_repo import SQLrepository
from back.models.relationships import project_user
from back.models.structures import Projects
from back.models.user import Users
import logging
from werkzeug.security import generate_password_hash


logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db):
        self.repo = SQLrepository(db)
        
    def get_user_by_login(self,login):
        filters = [Users.login == login]
        user = self.repo.get_one(Users, filters)
        if user:
            return user
        return None
    def get_user_by_id(self,id):
        filters = [Users.id == id]
        user = self.repo.get_one(Users, filters)
        if user:
            return user
        return None
    def delete_user(self, user_id):
        try:
            filters = [Users.id == user_id]
            self.repo.delete(Users, filters)
            return {"success": True, "message": "User deleted successfully", "code": 1002}, 200
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return {"success": False, "message": "Error", "code": 2000}, 500  
    def create_user(self, data):
        if not all(k in data for k in ("login", "password", "email")):
            return {"success": False, "message": "Missing parameters", "code": 2000}, 400

        # Проверка, существует ли пользователь
        filters = [
            or_(Users.login == data.get("login"), Users.email == data.get("email"))
        ]
        if self.repo.exists(Users, filters):
            return {"success": False, "message": "User already exists", "code": 2000}, 400

        # Создание нового пользователя
        new_user = Users(
            login=data.get("login"),
            password_hash=generate_password_hash(data.get('password')),
            email=data.get("email")
        )
        try:
            self.repo.add(new_user)
            return {"success": True, "message": "User created successfully", "code": 1001}, 200
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {"success": False, "message": "Error", "code": 2000}, 500
        
    def add_user_to_project(self, data):
        """
        Добавляет пользователя в проект.
        """
        user_id = data.get('user_id')
        project_id = data.get('project_id')

        # Проверка существования пользователя
        user = self.repository.get_one(Users, [Users.id == user_id])
        if not user:
            return {"success": False, "message": "User not found", "code": 2009}, 404

        # Проверка существования проекта
        project = self.repository.get_one(Projects, [Projects.id == project_id])
        if not project:
            return {"success": False, "message": "Project not found", "code": 2010}, 404

        # Проверка, не добавлен ли уже пользователь в проект
        existing_member = self.repository.exists(project_user, [project_user.c.project_id == project_id, project_user.c.user_id == user_id])
        if existing_member:
            return {"success": False, "message": "User already in project", "code": 2000}, 400

        try:
            # Добавляем пользователя в проект
            self.repository.insert_dynamic(project_user, {'project_id': project_id, 'user_id': user_id})
            return {"success": True, "message": "User added to project", "code": 1001}, 200
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding user to project: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}", "code": 2011}, 500

    def remove_user_from_project(self, data):
        """
        Удаляет пользователя из проекта.
        """
        user_to_delete_id = data.get("user_to_delete_id")
        project_id = data.get("project_id")

        # Проверка, существует ли такая связь (пользователь в проекте)
        pr_user = self.repository.get_one(project_user, [project_user.c.user_id == user_to_delete_id, project_user.c.project_id == project_id])
        if not pr_user:
            return {"success": False, "message": "User not found in project", "code": 2000}, 404

        try:
            # Удаляем пользователя из проекта
            self.repository.delete(project_user, [project_user.c.user_id == user_to_delete_id, project_user.c.project_id == project_id])
            return {"success": True, "message": "User removed from project", "code": 1001}, 200
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error removing user from project: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}", "code": 2000}, 500