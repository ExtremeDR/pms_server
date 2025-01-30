from back.infrastructure.repositories.sqlalchemy_repo import SQLrepository
from back.models.user import TMP_code, Users_tg


class TelegramUserController:
    def __init__(self, db):
        self.repo = SQLrepository(db)

    def generate_code(self, user_id, unique_code):
        """
        Генерация уникального кода для пользователя.
        """
        # Проверка, существует ли код или зарегистрирован ли пользователь в Telegram
        if self.repo.get_one(TMP_code, [TMP_code.user_id == user_id]):
            return {"success": False, "message": "Code already generated", "code": 2000}, 400
        
        if self.repo.get_one(Users_tg, [Users_tg.user_id == user_id]):
            return {"success": False, "message": "User already registered in Telegram", "code": 2000}, 400

        new_tmp_code = TMP_code(
            user_id=user_id,
            unic_code=unique_code
        )
        try:
            self.repo.add(new_tmp_code)
            return {"success": True, "message": "Code generated successfully", "code": 1001}, 200
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}", "code": 2000}, 500

    def add_telegram_user(self, tg_id, unique_code):
        """
        Добавление пользователя Telegram.
        """
        tmp_code = self.repo.get_one(TMP_code, [TMP_code.unic_code == unique_code])
        if not tmp_code:
            return {"success": False, "message": "Code not found", "code": 404}, 404

        user_id = tmp_code.user_id
        new_user_tg = Users_tg(
            user_id=user_id,
            user_tg_id=tg_id
        )
        try:
            self.repo.db.session.delete(tmp_code)
            self.repo.add(new_user_tg)
            return {"success": True, "message": "User linked successfully", "code": 1001}, 200
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}", "code": 2000}, 500

    def check_telegram_id(self, tg_id):
        """
        Проверка, зарегистрирован ли Telegram ID.
        """
        user_exists = self.repo.get_one(Users_tg, [Users_tg.user_tg_id == tg_id])
        return {
            "success": True,
            "message": "User exists" if user_exists else "User does not exist",
            "exists": bool(user_exists),
            "code": 1001
        }, 200