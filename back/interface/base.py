from flask import Blueprint
from back.interface.routers.project import router as project_blueprint
from back.interface.routers.user import router as user_blueprint
from back.interface.routers.tag import router as tag_blueprint
from back.interface.routers.task import router as task_blueprint
from back.interface.routers.sprint import router as sprint_blueprint

router = Blueprint('main_router', __name__, url_prefix='/api-v2')

router.register_blueprint(project_blueprint)
router.register_blueprint(user_blueprint)
router.register_blueprint(tag_blueprint)
router.register_blueprint(task_blueprint)
router.register_blueprint(sprint_blueprint)