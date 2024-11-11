import requests
import app.config as config
data = {
    "tg_id" : "12345678",
    "uniqueCode" : "234",
}

data2 ={
    "user_id" : "2",
    "uniqueCode" : "qwert",
}

data3 = {
    "login" : "login123",
    "pass" : "password123",
    "email" : "aboba@gmail.com",
}
# Artemka pass = 23vrcxw4rs
# Dimka pass = 13523r
data4 = {
    "login" : "login123",
    "password" : "password123",
}

data5 = {
    "description" : "Задание, в котором требуются знания языка SQL и умения работы с БД",
    "tag_name" : "SQL",
}

data6 = {
    "user_id" : 1,
    "project_title" : "Проект Project Management Studio",
    "project_description" : "Система «Project Management Studio» предназначена для организации командной деятельности в проектах, где предусмотрено наличие команд и разбиение деятельности на задачи.",
}

data7 = {
    "user_id" : 1,
}

tasks_by_sprint_id = {
    "sprint_id" : 1,
}
#r = requests.get(f"{config.base_url}/projects_by_head_id/{config.code_for_API}", json=data7)
#print(r.json())
#data = r.json()
#project_ids = [project["id"] for project in data["data"]]
#first_project_id = project_ids[0] if project_ids else None
data9 = {
    "sprint_id" : 1,
    "user_id" : 2,
    "name" : "Задание для Димки",
    "task_description" : "Описываю это задание",
    "task_duration" : 7,
    "tags_ids" : [1],
}
#response = requests.post(f"{config.base_url}/create_task/{config.code_for_API}", json=data9)
#response = requests.get(f"{config.base_url}/tasks_by_sprint_id/{config.code_for_API}", json=tasks_by_sprint_id)
#response = requests.post(f"{config.base_url}/add_user_to_project/{config.code_for_API}", json=data10)
#response = requests.post(f"{config.base_url}/create_sprint/{config.code_for_API}", json=data8)
#print(response.json())
#response = requests.post(f"{config.base_url}/create_project/{config.code_for_API}", json=data6)
#response = requests.get(f"{config.base_url}/generate-code/{config.code_for_API}", json=data2)
response = requests.post(f"{config.base_url}/is-user-exists/{config.code_for_API}", json=data4)
#response = requests.post(f"{config.base_url}/add-user/{config.code_for_API}", json=data3)
#response = requests.post(f"{config.base_url}/create_tag/{config.code_for_API}", json=data5)
#print(response.json())
#response = requests.post(f"{config.base_url}/add-tg-user", json=data)

data11 = {
    'tg_id':755525413
}
#response = requests.post(f"{config.base_url}/check_telegram_id", json={"telegramID": 123456782})
#response = requests.get(f"{config.base_url}/all_projects_by_tg_id/{config.code_for_API}", json=data11)
# deleting = {
#     "user_id" : 1,
#     "user_to_delete" : 2,
#     "pr_id" : 2,
# }
# response = requests.delete(f"{config.base_url}/delete_user_from_project/{config.code_for_API}", json=deleting)
# print(response.json())
# response = requests.post(f"{config.base_url}/add-user", json=data3)
print(response.json())