import argparse
import json

from runner.client import ConformanceClient
from runner.test_plan import TestPlanManager
from runner.executor import TestExecutor
from runner.results import ResultNormalizer


BASE_URL = "https://localhost.emobix.co.uk:8443"


def load_config(component: str):
    with open(f"configs/{component}.json", "r", encoding="utf-8") as file:
        return json.load(file)


def run_component(component: str):
    config = load_config(component)

    client = ConformanceClient(BASE_URL, verify_ssl=False)

    try:
        plan_manager = TestPlanManager(client)
        executor = TestExecutor(client)
        normalizer = ResultNormalizer()

        print(f"Running {component} conformance test...")

        # 1. Create configured plan
        plan = plan_manager.create_plan(
            config["plan"],
            config["configuration"],
            config["plan_variant"]
        )

        plan_id = plan["id"]

        print(f"Configured plan: {plan_id}")

        # 2. Create test execution
        test = plan_manager.create_test_from_plan(
            plan_id,
            config["test"],
            config["test_variant"]
        )

        module_id = test["id"]

        print(f"Test execution: {module_id}")

        # 3. Start + poll
        state = executor.run(module_id)

        print(f"Final state: {state}")

        # 4. Retrieve result
        module_info = client.get(
            f"/api/info/{module_id}"
        ).json()

        test_log = client.get(
            f"/api/log/{module_id}"
        ).json()

        print("\nRAW TEST LOG")
        print(json.dumps(test_log, indent=2))

        # 5. Normalize
        result = normalizer.normalize(
            module_info,
            test_log
        )

        print("\nRESULT")
        print(json.dumps(result, indent=2))

                # 6. Benchmark gate
        benchmark_passed, regressions = normalizer.check_benchmark(
            component,
            result
        )

        if benchmark_passed:
            print("\nBENCHMARK: PASS")
        else:
            print("\nBENCHMARK: FAIL")
            for regression in regressions:
                print(f"- {regression}")

            raise RuntimeError("Conformance benchmark regression detected")

    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--component", required=True, choices=["certify", "verify"])

    args = parser.parse_args()

    run_component(args.component)