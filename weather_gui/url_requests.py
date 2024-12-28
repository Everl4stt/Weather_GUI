import requests
from configs import URL, API_METHOD, KEY
from tkinter import messagebox
from io import BytesIO
from PIL import Image


# Получения данных о погоде через API сайта
def get_weather(city):
    params = {
        'key': KEY,
        'q': city,
        'days': 5,
    }
    uri = f'{URL}{API_METHOD}'
    response = requests.get(uri, params=params)
    if response.ok:
        data = response.json()
        return data
    return messagebox.showerror("Ошибка", "Введенные данные не корректны")

# Получение картинки по запросу
def get_image(url):
    response = requests.get(f'https:{url}')
    if response.ok:
        return Image.open(BytesIO(response.content))
    return Image.open('static/default.png')




