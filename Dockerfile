FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей для Tkinter и X11
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY . .

# Проверка зависимостей при запуске
RUN python3 -c "import tkinter; import sqlite3; print('✓ All dependencies installed')"

# Запуск приложения
CMD ["python3", "main.py"]
