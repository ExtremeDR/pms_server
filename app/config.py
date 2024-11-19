import os

path = r"D:\\Programming\\NGROK\\ngrok.exe"

class Config(object):
    base_url = os.environ.get('base_url')
    code_for_API = os.environ.get('code_for_API')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL_ANOTHER')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


'''
Status for Projects
1 - active
2 - finish
3 - stopped

Status for Sprints
1 - active
2 - finish
3 - stopped

Status for Tasks
1 - active
2 - finish
3 - stopped
4 - on_check
'''

'''
types of Projects

1 - Project without sprints
2 - Project with sprints
3 - Project with main tasks, sprintst and subtasks in them

'''

'''
Error codes API 


#Answer ==> {'success': bool(), 'code': №}


№:

Correct
1001 - Успешно

Uncorrect
2000 - General (еще не описанная) error
2001 - Логин уже существует
2002 - Email уже существует
2003 - Ошибка при добавлении кода
2004 - Отсутствует Код и\или Telegram ID
2005 - Уникальный код не найден в бд
2006 - У такого user_id уже есть tg_id
2007 - Ошибка при привязке тг_id
2008 - Не все данные переданы
2009 - User not found
2010 - Project not found
2011 - User is already a member of the project
2012 - Недостаточно прав
2013 - User not found in project
'''