import os
from dotenv import load_dotenv

# Укажите путь к вашему файлу .env
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)
print(os.environ.get('SQLALCHEMY_ENGINE_OPTIONS'))