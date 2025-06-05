FROM python:3.11-slim

WORKDIR /code

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов
COPY . .

# Создание пользователя
RUN useradd -m myuser && \
    chown -R myuser:myuser /code
USER myuser

# Стандартная команда (переопределяется в docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]