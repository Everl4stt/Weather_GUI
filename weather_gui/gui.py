import customtkinter as ctk
from url_requests import get_weather, get_image
from datetime import datetime, timedelta
from tkinter import messagebox
import asyncio
import threading


# Асинхронный адаптер для выполнения корутин в tkinter
def run_asyncio_coroutine(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutine)


def run_gui():
    # Настройки окна
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Weather forecast")
    app.geometry("600x400")
    app.resizable(False, False)

    # Задний фон
    background_frame = ctk.CTkFrame(app, fg_color=("#FFD37A", "#FFB347"))
    background_frame.pack(fill="both", expand=True)

    # Поле для ввода города и кнопка для вывода погоды в городе
    city = ctk.CTkEntry(app, placeholder_text='Enter city', width=200)
    city.place(relx=0.45, rely=0.5, anchor='center')
    city.insert(0, "Омск")

    # Текущая погода
    weather_icon = ctk.CTkLabel(app, text="", fg_color=("#FFD37A", "#FFB347"))
    main_label = ctk.CTkLabel(background_frame, text="Please select city", font=("Arial", 32))
    main_label.place(relx=0.5, rely=0.1, anchor="center")
    weather_info = ctk.CTkLabel(background_frame, text="", font=("Arial", 14))

    # Сегодняшний день
    today_label = ctk.CTkLabel(background_frame, text=f'{datetime.now().strftime("%A")}', font=("Arial", 18))
    today_label.place(relx=0.5, rely=0.2, anchor='center')

    # Дата последнего обновления погоды
    update_label = ctk.CTkLabel(background_frame, text='', font=("Arial", 14))

    # Следующие 5 дней
    day_labels = []
    icon_labels = []
    temp_labels = []
    for i in range(5):
        day_label = ctk.CTkLabel(background_frame, text=(datetime.now() + timedelta(days=i + 1)).strftime('%a'), font=("Arial", 14))
        day_labels.append(day_label)

        icon_label = ctk.CTkLabel(app, text='')
        icon_labels.append(icon_label)

        temp_label = ctk.CTkLabel(background_frame, text='')
        temp_labels.append(temp_label)

    # Асинхронное обновление данных погоды
    async def async_update_app():
        data = await asyncio.to_thread(get_weather, city.get())
        if data:
            next_days(data)
            main_label.configure(text=data['current']['temp_c'])
            weather_info.configure(text=f'{data["current"]["condition"]["text"]}\nWind: {data["current"]["wind_kph"]}\n'
                                        f'Pressure: {data["current"]["pressure_mb"]} mb')
            weather_info.place(relx=0.5, rely=0.3, anchor="center")
            current_weather_icon = ctk.CTkImage(get_image(data['current']['condition']['icon']), size=(80, 80))
            update_label.configure(text=f'Latest update:\n {data["current"]["last_updated"]} local time')
            update_label.place(relx=0.83, rely=0.05, anchor='center')
            weather_icon.configure(image=current_weather_icon)
            weather_icon.place(relx=0.2, rely=0.05)
            app.after(3600000, lambda: threading.Thread(target=run_asyncio_coroutine, args=(async_update_app(),)).start())
        else:
            messagebox.showerror("Ошибка", "Введенные данные не корректны")

    # Запуск асинхронной функции
    def update_app():
        threading.Thread(target=run_asyncio_coroutine, args=(async_update_app(),)).start()

    # Кнопка отображения погоды
    city_button = ctk.CTkButton(app, text="Show Weather", command=update_app)
    city_button.place(relx=0.65, rely=0.5, anchor="center")

    # Прогноз на 5 дней
    def next_days(data):
        for i in range(5):
            next_days_icon = ctk.CTkImage(get_image(data['forecast']['forecastday'][i]['day']['condition']['icon']), size=(40, 40))
            day_labels[i].configure(text=(datetime.now() + timedelta(days=i + 1)).strftime('%a'), font=("Arial", 14))
            day_labels[i].place(relx=0.11 + i * 0.18, rely=0.6)
            icon_labels[i].configure(image=next_days_icon, text="", fg_color=("#FFD37A", "#FFB347"))
            icon_labels[i].place(relx=0.1 + i * 0.18, rely=0.65)
            temp_labels[i].configure(text=data['forecast']['forecastday'][i]['day']['avgtemp_c'], font=("Arial", 14))
            temp_labels[i].place(relx=0.11 + i * 0.18, rely=0.75)

    # Автоматическое обновление при запуске
    app.after(10, update_app)

    app.mainloop()
