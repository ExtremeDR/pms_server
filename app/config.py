import os

base_url = os.environ.get('base_url')
code_for_API = os.environ.get('code_for_API')

class Config(object):
    DB_URL_ANOTHER = os.environ.get('DB_URL_ANOTHER')
    
    SQLALCHEMY_DATABASE_URI = DB_URL_ANOTHER
    SECRET_KEY = '21242341vfwdefwf3s'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

'''
1.	Добавление юзера
    a.	Отправляю json c login, password, email
    b.	Получаю json с результатом выполнения операции (message)
2.	Проверка юзера на наличие в базе
    a.	Отправляю json c login, password
    b.	Получаю json c результатом выполнения операции (true/false, message)
3.	Добавление проекта 
    a.	Отправляю json c title, description, sprintsID (в виде json), headID, membersID (в виде json)
    b.	 Получаю json с результатом выполнения операции (message)
4.	Добавление задачи
    a.	Отправляю json с description, userID, tagsID
    b.	Получаю json с результатом выполнения операции (message)
5.	Добавление спринта
    a.	Отправляю json с startDate, endDate, tasksID (в виде json)
    b.	Получаю json с результатом выполнения операции (message)
6.	Добавление тега
    a.	Отправляю json с name
    b.	Получаю json с результатом выполнения операции (message)

'''

'''
Error codes API 


#Answer ==> {'success': bool(), 'code': №}


№:

Correct
1001 - Успешно

Uncorrect
2000 - General (not discribed) error
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