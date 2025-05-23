#!/usr/bin/env python3
import os
import base64
from github import Github

# ——— Конфигурация ———
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # будем брать из переменной окружения
REPO_NAME = "optimas-backend"
REPO_DESCRIPTION = "Backend part of the OptiMassFit thesis project"
LOCAL_BACKEND_PATH = "./backend"          # относительный путь к папке с бэком

# ——— Подключаемся к GitHub ———
g = Github(GITHUB_TOKEN)
user = g.get_user()

# ——— Создаём репозиторий (или берём существующий) ———
try:
    repo = user.create_repo(
        name=REPO_NAME,
        description=REPO_DESCRIPTION,
        private=False
    )
    print(f"Repository '{REPO_NAME}' created.")
except Exception:
    repo = user.get_repo(f"{user.login}/{REPO_NAME}")
    print(f"Using existing repo '{REPO_NAME}'.")

# ——— Загружаем файлы из папки backend ———
for root, dirs, files in os.walk(LOCAL_BACKEND_PATH):
    for filename in files:
        local_path = os.path.join(root, filename)
        # путь в репозитории (относительно корня backend)
        repo_path = os.path.relpath(local_path, LOCAL_BACKEND_PATH).replace("\\", "/")

        with open(local_path, "rb") as f:
            content = f.read()

        try:
            repo.create_file(
                path=repo_path,
                message=f"Add {repo_path}",
                content=content
            )
            print(f"Uploaded: {repo_path}")
        except Exception as e:
            # файл уже есть или другая ошибка — просто сообщим и пропустим
            print(f"Skipped {repo_path}: {e}")

print("Done.")
