import requests


data1 = {
    'login': "User2",
    'password':"12345",
    'email':"ekgfnkesn@gmail.com",
}

data2 = {
    'login':"User2",
    'password':"12345",
}

data3 = {
    'user_id':"2",
    'project_title':"Первый проект всея руси",
    'project_description':"Хули, ничего не делаем, просто отдыхаем",
}

code_for_API = "3i7r4ybfwbatro387"
base_url = 'https://extremedr2.eu.pythonanywhere.com'

# ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ
#response = requests.post(f"{base_url}/add-user/{code_for_API}", json=data1) 

#Проверка на существование
#response = requests.post(f"{base_url}/is-user-exists/{code_for_API}", json=data2)

#
response = requests.post(f"{base_url}/create-project/{code_for_API}", json=data3)
print(response.status_code)
print(response.text)