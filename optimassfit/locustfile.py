from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)              # задержка между запросами
    host = "http://127.0.0.1:8000"         # адрес вашего Django-сервера

    def on_start(self):
        """
        Этот метод выполняется один раз при старте каждого виртуального пользователя:
        делаем логин, сохраняем токен.
        """
        resp = self.client.post(
            "/api/login/",
            json={"username": "TestUser1", "password": "TryPass12"},
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        token = resp.json()["token"]
        # сохраним заголовок для всех следующих запросов
        self.auth_headers = {"Authorization": f"Token {token}"}

    @task(5)
    def get_dashboard(self):
        """GET защищённого эндпоинта /api/profile/dashboard/"""
        self.client.get("/api/dashboard/", headers=self.auth_headers)

    @task(3)
    def get_plans(self):
        """GET списка всех своих планов"""
        self.client.get("/api/plans/", headers=self.auth_headers)

    @task(2)
    def update_profile(self):
        """POST /api/profile/update/ — обновить профиль и создать новый план"""
        payload = {
            "age": 30,
            "height": 180,
            "weight": 75,
            "goal": "maintain",
            "training_level": "2-3",
            "target_months": 3
        }
        self.client.post(
            "/api/profile/update/",
            json=payload,
            headers={**self.auth_headers, "Content-Type": "application/json"}
        )
