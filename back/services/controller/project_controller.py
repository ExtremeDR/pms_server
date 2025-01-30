from datetime import datetime, timedelta
import logging

from sqlalchemy import or_
from back.infrastructure.repositories.sqlalchemy_repo import SQLrepository
from back.models.relationships import project_user
from back.models.structures import Projects, Sprints, Tasks
from back.models.user import Users, Users_tg


logger = logging.getLogger(__name__)

class ProjectController:
    def __init__(self, repository: SQLrepository):
        self.repository = repository

    def get(self, project_id):
        """
        Получает проект по ID.
        :param project_id: ID проекта.
        :return: Объект проекта.
        """
        try:
            project = self.repository.get_one(Projects, [Projects.id == project_id])
            if project:
                return project
            else:
                raise ValueError("Project not found")
        except Exception as e:
            logger.error(f"Error fetching project with id {project_id}: {str(e)}")
            raise Exception(f"Error fetching project: {str(e)}")

    def user_id_from_tg_id(self,tg_id) -> int:
        fields = [Users_tg.user_id]
        filters = [Users_tg.user_tg_id == tg_id]
        user_query = self.repository.execute_dynamic_query(fields=fields, filters=filters)
        user_id = user_query.scalar()
        return user_id

    def get_projects_by_user_id(self, user_id):
        """
        Получает проекты по user_id из базы данных с использованием SQLrepository.
        :param user_id: ID пользователя, для которого нужно получить проекты.
        :return: Список проектов.
        """
        table = Projects

        fields = [
            table.id, table.title, table.description, table.status, table.start_date, table.head_id,
        ]

        joins = [
            (project_user, project_user.c.project_id == table.id, True)
        ]

        filters = [
            or_(
                table.head_id == user_id,
                project_user.c.user_id == user_id
            )
        ]

        def map_results(results):
            projects = []
            for row in results:
                project = {
                    "id": row.id,
                    "title": row.title,
                    "status": row.status,
                    "description": row.description,
                    "start_date": row.start_date,
                    "role": row.head_id == user_id  # Если user_id является head, то роль True
                }
                projects.append(project)
            return projects

        # Используем метод execute_dynamic_query для выполнения запроса
        try:
            res = self.repository.execute_dynamic_query(fields=fields, filters=filters, joins=joins, result_mapper=map_results)
            return res
        except Exception as e:
            logger.error(f"Error getting projects by user_id {user_id}: {str(e)}")
            raise Exception(f"Error getting projects: {str(e)}")
        
    def create_project(self, data):
        """
        Логика для создания проекта с использованием репозитория.
        """
        # Проверка наличия обязательных данных
        if self.check_data("user_id", "project_title", "project_description", data=data):
            return {'success': False, 'message': "Miss parameter(s)", 'code': 2000}, 400

        new_project = Projects(
            title=data.get("project_title"),
            head_id=data.get("user_id"),
            description=data.get("project_description"),
            start_date=datetime.now() + timedelta(hours=3),
            status=1,
        )

        try:
            # Используем метод add из репозитория для добавления нового проекта в базу данных
            self.repository.add(new_project)
            return {'success': True, 'message': "All good", 'code': 1001}, 200
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return {'success': False, 'message': f"Error: {str(e)}", 'code': 2000}, 500
        
    def get_head_id_by_project_id(self, project_id):
        """
        Логика для получения ID главы проекта по ID проекта.
        """
        try:
            # Проверка, существует ли проект с таким ID
            project = self.repository.get_one(Projects, [Projects.id == project_id])
            if not project:
                return {'success': False, 'message': "Project not found", 'code': 2000}, 404

            # Возвращаем ID главы проекта
            return {'success': True, 'head_id': project.head_id, 'code': 1001}, 200
        except Exception as e:
            logger.error(f"Error fetching project head: {str(e)}")
            return {'success': False, 'message': f"Error: {str(e)}", 'code': 2000}, 500
        
    def change_project_status_and_sprints(self, status, project_id):
        """
        Логика для изменения статуса проекта и связанных с ним спринтов и задач.
        """
        # Проверка входных параметров
        if not isinstance(status, int) or not project_id:
            return {'success': False, 'message': "Missing parameters or invalid status", 'code': 2000}, 400

        try:
            # Получаем проект
            project = self.repository.get_one(Projects, [Projects.id == project_id])
            if not project:
                return {'success': False, 'message': "Project not found", 'code': 2000}, 404

            # Изменяем статус проекта
            project.status = status

            # Получаем активные спринты для этого проекта
            sprints = self.repository.execute_dynamic_query(
                fields=[Sprints], 
                filters=[Sprints.project_id == project_id, Sprints.status == 1]
            ).scalars().all()

            # Обновляем статус спринтов и связанных с ними задач
            for sprint in sprints:
                sprint.status = 3  # Изменяем статус спринта на 3
                tasks = self.repository.execute_dynamic_query(
                    fields=[Tasks], 
                    filters=[Tasks.sprint_id == sprint.id]
                ).scalars().all()
                for task in tasks:
                    if task.status != 2:  # Если статус задачи не завершен (не равен 2)
                        task.status = 3  # Обновляем статус задачи на 3

            # Сохраняем изменения в базе данных
            self.repository.db.session.commit()

            return {'success': True, 'message': "Status updated successfully", 'code': 1001}, 200
        except Exception as e:
            # В случае ошибки откатываем транзакцию
            self.repository.db.session.rollback()
            logger.error(f"Error changing project status and sprints: {str(e)}")
            return {'success': False, 'message': f"Error: {str(e)}", 'code': 2000}, 500
        
    def get_users_in_project(self, project_id):
        """
        Получение списка пользователей в проекте, включая главу проекта.
        """
        # Проверка наличия параметра project_id
        if not project_id:
            return {'success': False, 'message': "Missing project_id", 'code': 2000}, 404

        try:
            # Формируем запрос для получения пользователей в проекте
            fields = [
                project_user.c.user_id.label("user_id"),
                Users.login.label("username"),
                (project_user.c.user_id == Projects.head_id).label("role"),
            ]
            joins = [
                (Users, Users.id == project_user.c.user_id, False),
                (Projects, Projects.id == project_user.c.project_id, False)
            ]
            filters = [
                project_user.c.project_id == project_id,
            ]

            def map_results(results):
                return [
                    {
                        "user_id": row.user_id,
                        "username": row.username,
                        "role": row.role
                    }
                    for row in results
                ]

            # Выполняем запрос на получение пользователей
            res = self.repository.execute_dynamic_query(fields=fields, filters=filters, joins=joins, result_mapper=map_results)

            # Получаем главу проекта
            head_project = self.repository.execute_dynamic_query(
                fields=[Projects.head_id], 
                filters=[Projects.id == project_id]
            ).scalars().first()

            if not head_project:
                return {'success': False, 'message': "Project head not found", 'code': 2000}, 404

            head_user = self.repository.execute_dynamic_query(
                fields=[Users.id, Users.login], 
                filters=[Users.id == head_project]
            )

            # Добавляем главу проекта в начало списка
            user = [{"user_id": head.id, "username": head.login, "role": True} for head in head_user]
            res += user

            return {'success': True, 'data': res, 'code': 1001}, 200

        except Exception as e:
            logger.error(f"Error fetching users in project: {str(e)}")
            return {'success': False, 'message': "Error: " + str(e), 'code': 2000}, 500