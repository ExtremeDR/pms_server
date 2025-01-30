import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

class Config(object):
    code_for_API = os.environ.get('code_for_API')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY= os.environ.get('SECRET_KEY')