# Используем официальный Python-образ
FROM python:3.12-slim

# Установка зависимостей
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Копируем проект
COPY . /app
WORKDIR /app

# Открываем порт Streamlit
EXPOSE 8501

# Запуск Streamlit
CMD ["streamlit", "run", "🌍_General.py", "--server.port=8501", "--server.address=0.0.0.0"]
