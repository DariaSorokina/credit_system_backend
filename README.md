# Credit Conveyor

Микросервис для обработки кредитных заявок

## Установка

1. Создать виртуальное окружение:
```bash
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate    # Windows#
uvicorn main:app --reload

1.Проверьте статус контейнеров

docker-compose ps

2. Просмотрите логи проблемного контейнера
Для основного сервиса:

docker-compose logs web

ля всех сервисов:

bash
docker-compose logs

После обновления файлов выполните:

docker-compose down
docker-compose build --no-cache
docker-compose up
