import requests

# Надежный публичный API с интересными фактами (работает всегда)
url = "https://catfact.ninja/fact"

print("Стучимся на внешний сервер...")

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Сервер успешно ответил!")
    print(f"Случайный факт: {data['fact']}")
else:
    print(f"Ошибка запроса: статус {response.status_code}")