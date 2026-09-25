from locust import HttpUser, between, task


class HealthCheckUser(HttpUser):
    """
    Basic load-test user for measuring HTTP/server performance.
    """

    wait_time = between(1, 2)

    @task
    def health_check(self):
        self.client.get(
            "/healthz/",
            name="/healthz/",
        )
