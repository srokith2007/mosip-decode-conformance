import time

from runner.client import ConformanceClient


class TestExecutor:

    def __init__(self, client: ConformanceClient):
        self.client = client

    def start(self, module_id: str):
        response = self.client.post(
            f"/api/runner/{module_id}"
        )

        return response.json()

    def wait_for_completion(
        self,
        module_id: str,
        timeout: int = 300,
        poll_interval: int = 2
    ):
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.client.get(
                f"/api/runner/{module_id}/wait-state",
                params={
                    "states": "FINISHED,INTERRUPTED",
                    "timeoutMs": poll_interval * 1000
                }
            )

            data = response.json()

            state = data.get("state")

            if state in ("FINISHED", "INTERRUPTED"):
                return state

        return "TIMEOUT"

    def run(self, module_id: str):
        self.start(module_id)

        return self.wait_for_completion(module_id)