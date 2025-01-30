from datetime import datetime, timedelta
from back.infrastructure.repositories.sqlalchemy_repo import SQLrepository
from back.models.structures import Sprints

class SprintController:
    def __init__(self, repository: SQLrepository):
        self.repository = repository

    def get_sprints(self, project_id):
        """
        Получение списка спринтов по project_id.
        """
        try:
            table = Sprints
            fields = [
                table.id, table.start_date, table.end_date, table.status,
                table.project_id
            ]
            filters = [table.project_id == project_id]

            def map_results(results):
                sprints = []
                for row in results:
                    sprints.append({
                        "id": row.id,
                        "start_date": row.start_date,
                        "end_date": row.end_date,
                        "status": row.status
                    })
                return sprints

            res = self.repository.execute_dynamic_query(fields=fields, filters=filters, result_mapper=map_results)
            return {'success': True, 'data': res, 'code': 1001}, 200
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}", 'code': 2000}, 404

    def create_sprint(self, project_id, sprint_duration):
        """
        Создание нового спринта.
        """
        try:
            new_sprint = Sprints(
                start_date=datetime.now() + timedelta(hours=3),
                status=1,
                end_date=datetime.now() + timedelta(hours=3) + timedelta(days=sprint_duration),
                project_id=project_id
            )

            self.repository.add(new_sprint)
            return {'success': True, 'message': 'Sprint created successfully', 'code': 1001}, 200
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}", 'code': 2000}, 500

    def update_sprint_status(self, sprint_id, new_status):
        """
        Обновление статуса спринта.
        """
        try:
            sprint = self.repository.get_one(Sprints, [Sprints.id == sprint_id])
            if not sprint:
                return {'success': False, 'message': 'Sprint not found', 'code': 2000}, 404

            sprint.status = new_status
            self.repository.db.session.commit()
            return {'success': True, 'message': 'Sprint status updated', 'code': 1001}, 200
        except Exception as e:
            self.repository.db.session.rollback()
            return {'success': False, 'message': f"Error: {str(e)}", 'code': 2000}, 500