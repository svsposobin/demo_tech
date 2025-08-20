🔶 DEMO-TECH
---
---

## ⚠️ Примечания:

> **Советуется пересмотреть параметры подключения к postgres и, настроить их под себя, если необходимо.**
> **Базово сервис работает на:**
> 
> **POSTGRES_HOST=localhost**
> 
> **POSTGRES_PORT=5432**
> 
> **POSTGRES_USER=postgres**
> 
> **POSTGRES_PASSWORD=postgres**
> 
> **POSTGRES_DATABASE=postgres**
> 
> **Настройка находится в корневой зоне сервиса в переменных окружения -> .env.test**

## 🔹 Старт через Docker (Рекомендуется):

#### **Остановить postgres-сервис во избежание проблем с портами в контейнере:**

```bash
task stop_postgres_service
```

#### **Создать сеть для контейнеров:**

```bash
task create_docker_network
```

#### **Собрать сборку:**

```bash
task build_docker
```

### Открыть адрес документации FastAPI (Для удобства) -> http://0.0.0.0:8000/docs , Тестировать функционал

#### Credentials пользователей в базовой миграции:

```
1. Admin:
email: admin@admin.admin
password: admin

2. Users
email: test_user1@user.user ; test_user2@user.user ; test_user3@user.user ; test_user4@user.user
password: user (У всех один)
```

---

---

> **Доп команды:**

**Проверить контейнеры**

```bash
task check_containers
```

**Запустить основной сервис, если базово не включился**

```bash
task run_service
```

**Остановить контейнеры:**

```bash
task stop_service
```

**Удалить контейнеры: (Внимание: Удаляет также образ postgres:16.3-alpine3.19)**

```bash
task delete_containers
```

**Удалить сеть для контейнеров:**

```bash
task delete_docker_network
```

**Включить postgres-сервисы**

```bash
task start_postgres_service

```

---

## 🔹 Локальный старт:

#### **Установить зависимости (Не забывая про .venv)**:

```bash
pip install -r requirements.txt
```

#### **'Накатить' базовую миграцию:**

```bash
alembic upgrade 592c2bfc2ad5
```

#### **Запустить сервер:**:

```bash
python src/main.py
```

### Открыть адрес документации FastAPI (Для удобства) -> http://0.0.0.0:8000/docs , Тестировать функционал

#### Credentials пользователей в базовой миграции:

```
1. Admin:
email: admin@admin.admin
password: admin

2. Users
email: test_user1@user.user ; test_user2@user.user ; test_user3@user.user ; test_user4@user.user
password: user (У всех один)
```

---

## 🔹 Дополнительные инструменты:

#### **Линтер:**:

```bash
flake8 ./
```

#### **Типизатор:**

```bash
mypy ./
```

## 🔹 Дополнения:

> **Функционал не покрыт тестами, не было указано в условии тех. задания**
>
> **"Роут" register отсутствует, регистрации пользователя только через функционал администратора**
