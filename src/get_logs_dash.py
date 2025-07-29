import json

import requests

url = "http://46.229.141.86:44455/get_logs"

# Указываем название файла который нам нужен
search_request = {
    "log_name": "actual_july_logs.json",
}


response = requests.post(url, json=search_request)

if response.status_code == 200:
    data = response.json()
    # Сохраняем в JSON-файл
    with open("../data/log.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # Сами логи
    print(data["logs"])
    # Время последнего обновления
    print(data["time"])
