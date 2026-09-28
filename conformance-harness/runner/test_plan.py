import json

from runner.client import ConformanceClient


class TestPlanManager:

    def __init__(self, client: ConformanceClient):
        self.client = client

    def create_plan(self, plan_name: str, config: dict, variant: dict | None = None):
        params = {
            "planName": plan_name
        }

        if variant is not None:
            params["variant"] = json.dumps(variant)

        response = self.client.post(
            "/api/plan",
            params=params,
            content=json.dumps(config)
        )

        return response.json()

    def create_test_from_plan(
        self,
        plan_id: str,
        test_name: str,
        variant: dict | None = None
    ):
        params = {
            "test": test_name,
            "plan": plan_id
        }

        if variant is not None:
            params["variant"] = json.dumps(variant)

        response = self.client.post(
            "/api/runner",
            params=params
        )

        return response.json()