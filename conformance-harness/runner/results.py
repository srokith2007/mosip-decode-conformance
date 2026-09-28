import json
from pathlib import Path


class ResultNormalizer:

    def normalize(self, module_info: dict, test_log: list | dict):
        result = {
            "test_id": module_info.get("id"),
            "test_name": module_info.get("name"),
            "status": module_info.get("status"),
            "result": module_info.get("testmodule_result"),
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }

        if isinstance(test_log, list):
            for item in test_log:
                item_result = item.get("result")

                if item_result == "SUCCESS":
                    result["passed"] += 1

                elif item_result == "FAILURE":
                    result["failed"] += 1

                elif item_result == "WARNING":
                    result["warnings"] += 1

                if item_result == "FINISHED":
                    result["test_id"] = item.get(
                        "testId",
                        result["test_id"]
                    )

                    result["test_name"] = item.get(
                        "src",
                        result["test_name"]
                    )

                    result["status"] = "FINISHED"

                    result["result"] = item.get(
                        "testmodule_result",
                        result["result"]
                    )

        return result

    def check_benchmark(self, component: str, result: dict):
        benchmark_file = Path(__file__).resolve().parent.parent / "reports" / "benchmark.json"

        with open(benchmark_file, "r", encoding="utf-8") as file:
            benchmark = json.load(file)

        expected = benchmark[component]

        regressions = []

        expected_failures = expected.get("expected_failures", 0)

        if result["failed"] > expected_failures:
            regressions.append(
            f"Unexpected failures: {result['failed']} > "
            f"{expected_failures} expected"
        )

        if result["passed"] < expected["passed"]:
            regressions.append(
            f"Passed tests decreased: {result['passed']} < {expected['passed']}"
        )

        if result["warnings"] > expected["warnings"]:
            regressions.append(
            f"Warnings increased: {result['warnings']} > {expected['warnings']}"
        )

        return len(regressions) == 0, regressions