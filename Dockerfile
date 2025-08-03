FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Установка зависимостей
RUN pip install --upgrade pip

# 2. Установить torch отдельно, с указанием CPU-репозитория
RUN pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu

# 3. Установить остальные зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . /app
WORKDIR /app

# Открываем порт Streamlit
EXPOSE 8501

# Запуск Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
